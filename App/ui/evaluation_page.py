import streamlit as st

from config import MAX_MERIT_TOTAL, PASS_MARK
from services.leaderboard_service import load_data, save_data, recalculate_ranks
from services.evaluation_service import generate_marksheet_img


def render_evaluation_page():
    st.subheader("Enter Candidate Details & Scores")

    with st.form("evaluation_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            student_name = st.text_input("Candidate Name")
        with col_b:
            roll_no = st.text_input("Roll Number")

        st.markdown("**Papers**")
        c1, c2 = st.columns(2)
        with c1:
            p1 = st.number_input("P1 - English (out of 100)", min_value=0, max_value=100, step=1)
        with c2:
            p2 = st.number_input("P2 - Hindi (out of 100)", min_value=0, max_value=100, step=1)

        st.markdown("**Merit Subjects (P3-P6)**")
        c3, c4, c5, c6 = st.columns(4)
        with c3:
            p3 = st.number_input("P3", min_value=0, max_value=100, step=1)
        with c4:
            p4 = st.number_input("P4", min_value=0, max_value=100, step=1)
        with c5:
            p5 = st.number_input("P5", min_value=0, max_value=100, step=1)
        with c6:
            p6 = st.number_input("P6", min_value=0, max_value=100, step=1)

        submitted = st.form_submit_button("Evaluate & Save")

    if not submitted:
        return

    if not student_name.strip() or not roll_no.strip():
        st.error("Please enter both Candidate Name and Roll Number.")
        return

    merit_total = p3 + p4 + p5 + p6
    merit_pct = (merit_total / MAX_MERIT_TOTAL) * 100

    scores = {
        "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "p6": p6,
        "merit_total": merit_total,
        "merit_pct": merit_pct,
    }

    db = load_data()
    db = [item for item in db if str(item.get("roll_no", "")).strip() != roll_no.strip()]
    db.append({
        "name": student_name.strip(),
        "roll_no": roll_no.strip(),
        "merit_total": merit_total,
        "pct": merit_pct,
        "scores": scores,
    })

    db = recalculate_ranks(db)
    candidate = next(
        (item for item in db if str(item.get("roll_no", "")).strip() == roll_no.strip()),
        None,
    )
    if candidate:
        scores["rank"] = candidate["rank"]

    save_data(db)

    st.success(f"Evaluation Complete! Final Rank: #{scores['rank']} out of {len(db)} candidates.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("English (P1)", f"{p1}/100", "Passed" if p1 >= PASS_MARK else "Failed")
    m2.metric("Hindi (P2)", f"{p2}/100", "Passed" if p2 >= PASS_MARK else "Failed")
    m3.metric("Merit Score (P3-P6)", f"{merit_total}/{MAX_MERIT_TOTAL}")
    m4.metric("Overall Rank", f"#{scores['rank']} / {len(db)}")

    img_bytes = generate_marksheet_img(student_name, roll_no, scores)
    st.image(img_bytes, caption="Generated Official Marksheet")
    st.download_button(
        "📥 Download Official Marksheet Image",
        img_bytes,
        f"Marksheet_{roll_no}.png",
        "image/png",
    )
