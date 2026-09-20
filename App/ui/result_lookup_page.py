"""
Public-facing page: a candidate types in only their own roll number
and sees only their own result — never the full leaderboard. This is
the page meant to be shared with candidates directly.
"""

import streamlit as st
import pandas as pd

from config import PASS_MARK, PAPERS, QUALIFYING_PERCENT
from services.leaderboard_service import load_data
from services.evaluation_service import generate_marksheet_img


def render_result_lookup_page():
    st.subheader("🔍 Check Your Result")
    st.caption("Enter your Roll Number to view your result. No login required.")

    direct_roll = str(st.query_params.get("roll_no", "")).strip()
    roll_no_input = st.text_input("Roll Number", value=direct_roll, key="lookup_roll_no")

    if not (st.button("Check Result", key="lookup_button") or direct_roll):
        return

    roll_no = roll_no_input.strip()
    if not roll_no:
        st.error("Please enter your Roll Number.")
        return

    db = load_data()
    candidate = next(
        (r for r in db if str(r.get("roll_no", "")).strip() == roll_no),
        None,
    )

    if candidate is None:
        st.error("No result found for that Roll Number. Please check and try again.")
        return

    st.success(f"Result found for **{candidate.get('name', 'Candidate')}**")

    scores = candidate.get("scores", {}) or {}

    status = candidate.get("status", "Qualified")
    if status == "Disqualified":
        st.error("❌ STATUS: NOT QUALIFIED (failed English or Hindi qualifying cutoff)")
    else:
        st.success("✅ STATUS: QUALIFIED")

    c1, c2, c3, c4 = st.columns(4)
    rank = candidate.get("rank")
    c1.metric("Overall Rank", f"#{rank}" if rank else "N/A")
    c2.metric("Merit Score (P3-P6)", f"{candidate.get('raw_merit_total', candidate.get('merit_total', 0))}/{candidate.get('merit_max', 400)}")
    c3.metric("Merit Percentage", f"{candidate.get('pct', 0):.2f}%")
    c4.metric("Qualifying Status", status)

    papers = candidate.get("papers", {})
    if papers:
        rows = []
        for paper_id, meta in PAPERS.items():
            result = papers.get(paper_id, {})
            pct = float(result.get("percentage", 0))
            if meta["category"] == "Qualifying":
                paper_status = "Passed" if pct >= QUALIFYING_PERCENT else "Failed"
            else:
                paper_status = "Counted" if status == "Qualified" else "N/A (Merit Paper)"
            rows.append({
                "Paper": meta["code"], "Subject": meta["subject"], "Category": meta["category"],
                "Correct": result.get("correct", 0), "Wrong": result.get("wrong", 0),
                "Deleted": result.get("bonus", 0),
                "Score": f"{result.get('score', 0)} / {result.get('max_score', 0)}",
                "Percentage": f"{pct:.1f}%", "Status": paper_status,
            })
        st.markdown("### 📊 Subject-wise Score Breakdown")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    if not papers and (scores.get("p1") is not None or scores.get("p2") is not None):
        p1 = scores.get("p1", 0)
        p2 = scores.get("p2", 0)
        pc1, pc2 = st.columns(2)
        pc1.metric("English (P1)", f"{p1}/100", "Passed" if p1 >= PASS_MARK else "Failed")
        pc2.metric("Hindi (P2)", f"{p2}/100", "Passed" if p2 >= PASS_MARK else "Failed")

    comparison = candidate.get("comparison")
    if comparison:
        st.markdown("**Answer Sheet Comparison Summary**")
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Correct", comparison.get("correct", 0))
        cc2.metric("Incorrect", comparison.get("incorrect", 0))
        cc3.metric("Unanswered", comparison.get("unanswered", 0))
        cc4.metric("Accuracy", f"{comparison.get('accuracy', 0):.2f}%")

    # Only offer a generated marksheet image if we have full paper-wise scores
    if not papers and all(k in scores for k in ("p1", "p2", "p3", "p4", "p5", "p6")):
        result_scores = dict(scores)
        result_scores["rank"] = candidate.get("rank", "N/A")
        img_bytes = generate_marksheet_img(
            candidate.get("name", "Candidate"), roll_no, result_scores
        )
        st.image(img_bytes, caption="Your Marksheet")
        st.download_button(
            "📥 Download Marksheet",
            img_bytes,
            f"Marksheet_{roll_no}.png",
            "image/png",
            key="lookup_download",
        )
