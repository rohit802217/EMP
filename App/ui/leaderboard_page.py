import streamlit as st
import pandas as pd

from services.leaderboard_service import (
    load_data,
    save_data,
    recalculate_ranks,
    import_leaderboard_file,
)
from utils.auth import is_admin


def render_leaderboard_page():
    st.subheader("🏆 Live Candidate Ranking & Leaderboard")
    if st.button('Refresh leaderboard',key='refresh_leaderboard'):
        st.rerun()
    st.caption('App ranks are within the same exam and marking scheme, using complete reviewed qualified results. Equal scores share rank. Imported totals alone do not establish eligibility or official rank.')

    if is_admin():
        with st.expander("📂 Upload Candidate Leaderboard", expanded=False):
            st.markdown(
                """
                Upload a **CSV or Excel file**.

                Required columns: `name`, `roll_no`, `merit_total`

                Optional columns: `pct`, `p1`, `p2`, `p3`, `p4`, `p5`, `p6`
                """
            )

            leaderboard_file = st.file_uploader(
                "Choose leaderboard file", type=["csv", "xlsx", "xls"], key="leaderboard_upload"
            )

            if leaderboard_file:
                st.write(f"Selected file: **{leaderboard_file.name}**")

                if st.button("📥 Import Candidates", key="import_candidates"):
                    imported_records = import_leaderboard_file(leaderboard_file)

                    if imported_records is not None:
                        if not imported_records:
                            st.warning("No valid candidate records were found.")
                        else:
                            db = load_data()
                            added = 0
                            updated = 0

                            for record in imported_records:
                                roll = str(record["roll_no"]).strip()
                                found = False

                                for existing in db:
                                    if str(existing.get("roll_no", "")).strip() == roll:
                                        existing.update(record)
                                        found = True
                                        updated += 1
                                        break

                                if not found:
                                    db.append(record)
                                    added += 1

                            db = recalculate_ranks(db)
                            save_data(db)

                            st.success(f"Import complete — {added} added, {updated} updated.")
                            st.rerun()

    db = recalculate_ranks(load_data())

    if not db:
        st.info(
            "No candidate submissions recorded yet. Evaluate a candidate, "
            "import a leaderboard, or use Answer Sheet Comparison."
        )
        return

    df_rank = pd.DataFrame(db)
    if 'exam_id' in df_rank.columns:
        exam_filter=st.selectbox('Exam', ['All exams']+sorted(df_rank['exam_id'].dropna().unique().tolist()),key='leaderboard_exam')
        if exam_filter!='All exams':
            df_rank=df_rank[df_rank['exam_id']==exam_filter]
    else:
        df_rank['exam_id']='Unverified'
    for col in ["rank", "name", "roll_no", "merit_total", "pct"]:
        if col not in df_rank.columns:
            df_rank[col] = None

    search_term = st.text_input("🔎 Search by name or roll number", "", key="leaderboard_search")
    if search_term.strip():
        mask = (
            df_rank["name"].astype(str).str.contains(search_term, case=False, na=False,regex=False)
            | df_rank["roll_no"].astype(str).str.contains(search_term, case=False, na=False,regex=False)
        )
        df_rank = df_rank[mask]

    if "status" not in df_rank.columns:
        df_rank["status"] = "Unverified"
    # Keep earned marks visible even when the candidate is not eligible for rank.
    if 'raw_merit_total' in df_rank.columns:
        df_rank['merit_total']=df_rank['raw_merit_total'].fillna(df_rank['merit_total'])
    df_rank['pct']=df_rank.apply(lambda r: round(float(r['merit_total'])/float(r['merit_max'])*100,2)
                                if pd.notna(r.get('merit_max')) and float(r['merit_max'])>0 else r['pct'],axis=1)
    st.caption(f'{len(df_rank)} saved candidates shown.')
    df_display = df_rank[["rank", "exam_id", "name", "roll_no", "status", "merit_total", "pct"]].rename(columns={
        "exam_id": "Exam",
        "rank": "Rank",
        "name": "Candidate Name",
        "roll_no": "Roll Number",
        "status": "Status",
        "merit_total": "Merit Score",
        "pct": "Percentage (%)",
    }).sort_values("Rank", na_position="last")

    if is_admin():
        st.markdown("**Table is editable** — fix any name/roll number mix-ups directly, then click Save Changes.")
        edited_df = st.data_editor(
            df_display,
            width="stretch",
            disabled=["Rank", "Exam", "Status", "Merit Score", "Percentage (%)"],
            key="leaderboard_editor",
        )

        if st.button("💾 Save Changes", key="save_leaderboard_edits"):
            edits_by_original_roll = {
                str(orig): (str(new_name).strip(), str(new_roll).strip())
                for orig, new_name, new_roll in zip(
                    df_display["Roll Number"], edited_df["Candidate Name"], edited_df["Roll Number"]
                )
            }
            for record in db:
                orig_roll = str(record.get("roll_no", "")).strip()
                if orig_roll in edits_by_original_roll:
                    new_name, new_roll = edits_by_original_roll[orig_roll]
                    record["name"] = new_name
                    record["roll_no"] = new_roll
            save_data(db)
            st.success("Leaderboard updated.")
            st.rerun()
    else:
        st.dataframe(df_display, width="stretch")

    csv_bytes = df_display.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Leaderboard (CSV)", csv_bytes, "leaderboard.csv", "text/csv")

    if is_admin():
        if st.button("🗑️ Clear Leaderboard (Reset All Data)", key="clear_leaderboard"):
            save_data([])
            st.rerun()
