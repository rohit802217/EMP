import streamlit as st
import pandas as pd

from services.ocr_service import extract_text_from_file, OCR_AVAILABLE, PDF_AVAILABLE
from services.comparison_service import (
    parse_answers,
    answers_dict_to_df,
    dataframe_to_answer_map,
)
from services.leaderboard_service import update_leaderboard_from_comparison


def _highlight_result(row):
    if row["Result"] == "Correct":
        return ["background-color: #d4f7d4"] * len(row)
    if row["Result"] in ["Incorrect", "Unanswered"]:
        return ["background-color: #f7d4d4"] * len(row)
    if row["Result"] == "Deleted (Excluded)":
        return ["background-color: #f7f0d4"] * len(row)
    if row["Result"] == "Missing Answer Key":
        return ["background-color: #f7e0d4"] * len(row)
    return [""] * len(row)


def _render_upload_and_extract():
    name_col, roll_col = st.columns(2)
    with name_col:
        comparison_student_name = st.text_input(
            "🧑 Candidate Name",
            key="comparison_student_name",
            help="Enter the candidate's actual name — this is what will show in the leaderboard.",
        )
    with roll_col:
        comparison_roll_no = st.text_input(
            "🎓 Roll Number",
            key="comparison_roll_no",
            help=(
                "Enter a Roll Number. If it already exists it will be updated. "
                "If it does not exist, a new candidate will automatically be created."
            ),
        )

    col_left, col_right = st.columns(2)
    with col_left:
        paper_file = st.file_uploader(
            "Upload Answer Sheet (Paper)", type=["png", "jpg", "jpeg", "pdf"], key="paper_upload"
        )
    with col_right:
        key_file = st.file_uploader(
            "Upload Official Answer Key", type=["png", "jpg", "jpeg", "pdf"], key="key_upload"
        )

    st.markdown("**Marking scheme**")
    mark_col1, mark_col2 = st.columns(2)
    with mark_col1:
        marks_per_correct = st.number_input(
            "Marks per correct answer", min_value=0.0, value=1.0, step=0.25, key="marks_per_correct"
        )
    with mark_col2:
        negative_marks = st.number_input(
            "Negative marks per wrong/unanswered answer",
            min_value=0.0, value=0.0, step=0.25, key="negative_marks",
        )

    if paper_file and key_file:
        if st.button("🔍 Extract Answers from Both Files", key="extract_answers"):
            with st.spinner("Reading candidate answer sheet..."):
                paper_text = extract_text_from_file(paper_file)
                paper_answers = parse_answers(paper_text)

            with st.spinner("Reading official answer key..."):
                key_text = extract_text_from_file(key_file)
                key_answers = parse_answers(key_text)

            st.session_state["paper_answers"] = paper_answers
            st.session_state["key_answers"] = key_answers
            st.session_state["paper_ocr_text"] = paper_text
            st.session_state["key_ocr_text"] = key_text

            if not paper_answers:
                st.warning(
                    "Couldn't automatically detect Question/Answer pairs in the "
                    "answer sheet. You can add them manually below."
                )
            else:
                st.success(f"Detected {len(paper_answers)} candidate answers.")

            if not key_answers:
                st.warning(
                    "Couldn't automatically detect Question/Answer pairs in the "
                    "answer key. You can add them manually below."
                )
            else:
                st.success(f"Detected {len(key_answers)} answer-key entries.")

            with st.expander("🔎 Show OCR Text"):
                debug_col1, debug_col2 = st.columns(2)
                with debug_col1:
                    st.markdown("**Candidate OCR Text**")
                    st.text_area("Candidate OCR", paper_text, height=300, key="candidate_ocr_view")
                with debug_col2:
                    st.markdown("**Answer Key OCR Text**")
                    st.text_area("Key OCR", key_text, height=300, key="key_ocr_view")

    return comparison_student_name, comparison_roll_no, marks_per_correct, negative_marks


def _render_editor():
    st.markdown("---")
    st.subheader("Review & Correct Answers")
    st.info("You can add missing questions manually. Use A, B, C, D or DELETED.")

    edit_col1, edit_col2 = st.columns(2)

    with edit_col1:
        st.markdown("**Candidate's Answers**")
        paper_df = answers_dict_to_df(st.session_state.get("paper_answers", {}), "Candidate Answer")
        paper_df_edited = st.data_editor(
            paper_df,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Question": st.column_config.NumberColumn("Question", min_value=1, step=1),
                "Candidate Answer": st.column_config.SelectboxColumn(
                    "Candidate Answer", options=["A", "B", "C", "D"]
                ),
            },
            key="paper_editor",
        )

    with edit_col2:
        st.markdown("**Official Answer Key**")
        key_df = answers_dict_to_df(st.session_state.get("key_answers", {}), "Correct Answer")
        key_df_edited = st.data_editor(
            key_df,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Question": st.column_config.NumberColumn("Question", min_value=1, step=1),
                "Correct Answer": st.column_config.SelectboxColumn(
                    "Correct Answer", options=["A", "B", "C", "D", "DELETED"]
                ),
            },
            key="key_editor",
        )

    return paper_df_edited, key_df_edited


def _compare(paper_map, key_map):
    all_q = sorted(set(paper_map) | set(key_map))
    results = []
    correct_count = incorrect_count = unanswered_count = 0
    deleted_count = missing_key_count = 0

    for q in all_q:
        cand_ans = paper_map.get(q, "—")
        correct_ans = key_map.get(q, "—")

        if correct_ans == "DELETED":
            status = "Deleted (Excluded)"
            deleted_count += 1
        elif correct_ans == "—":
            status = "Missing Answer Key"
            missing_key_count += 1
        elif cand_ans == "—":
            status = "Unanswered"
            unanswered_count += 1
            incorrect_count += 1
        elif cand_ans == correct_ans:
            status = "Correct"
            correct_count += 1
        else:
            status = "Incorrect"
            incorrect_count += 1

        results.append({
            "Question": q, "Candidate Answer": cand_ans,
            "Correct Answer": correct_ans, "Result": status,
        })

    return pd.DataFrame(results), correct_count, incorrect_count, unanswered_count, deleted_count


def render_comparison_page():
    st.subheader("📄 Compare Answer Sheet vs Answer Key")
    st.caption(
        "Upload the candidate's answered paper and the official answer key. "
        "Extracted answers can be corrected manually before comparison."
    )

    comparison_student_name, comparison_roll_no, marks_per_correct, negative_marks = _render_upload_and_extract()

    if "paper_answers" in st.session_state or "key_answers" in st.session_state:
        paper_df_edited, key_df_edited = _render_editor()

        if st.button("✅ Compare Now", key="compare_now"):
            if not comparison_roll_no.strip():
                st.error("Please enter the Candidate Roll Number before clicking Compare Now.")
                st.stop()

            paper_map = dataframe_to_answer_map(paper_df_edited, "Candidate Answer")
            key_map = dataframe_to_answer_map(key_df_edited, "Correct Answer")

            if not key_map:
                st.error("No valid answers were found in the official answer key.")
                st.stop()

            results_df, correct_count, incorrect_count, unanswered_count, deleted_count = _compare(
                paper_map, key_map
            )

            total_scorable = correct_count + incorrect_count
            final_score = (correct_count * marks_per_correct) - (incorrect_count * negative_marks)
            final_score = round(max(0, min(400, float(final_score))), 2)
            accuracy = (correct_count / total_scorable * 100) if total_scorable else 0

            update_success, update_result = update_leaderboard_from_comparison(
                comparison_roll_no, final_score, correct_count, incorrect_count,
                unanswered_count, deleted_count, accuracy, comparison_student_name,
            )

            if update_success:
                updated_candidate = update_result["candidate"]
                action_text = "new candidate was created" if update_result["action"] == "created" else "candidate was updated"

                st.success(f"✅ Comparison complete and leaderboard {action_text}.")
                st.success(
                    f"🏆 Roll No: {comparison_roll_no} | "
                    f"Merit Score: {updated_candidate['merit_total']}/400 | "
                    f"Percentage: {updated_candidate['pct']:.2f}% | "
                    f"Rank: #{updated_candidate['rank']}"
                )
            else:
                st.warning("Comparison completed, but the leaderboard was not updated.")
                st.warning(str(update_result))

            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Scorable Questions", total_scorable)
            rc2.metric("Correct Answers", correct_count)
            rc3.metric("Accuracy", f"{accuracy:.2f}%")
            rc4.metric("Final Score", f"{final_score:.2f}/400")

            info1, info2, info3 = st.columns(3)
            info1.metric("Incorrect", incorrect_count)
            info2.metric("Unanswered", unanswered_count)
            info3.metric("Deleted / Excluded", deleted_count)

            if update_success:
                st.markdown("---")
                st.subheader("🏆 Updated Leaderboard Result")
                updated_candidate = update_result["candidate"]

                rank_col1, rank_col2, rank_col3 = st.columns(3)
                rank_col1.metric("Candidate", updated_candidate.get("name", "Unknown"))
                rank_col2.metric("New Rank", f"#{updated_candidate['rank']}")
                rank_col3.metric("Merit Score", f"{updated_candidate['merit_total']}/400")

                st.info(
                    "The leaderboard has been saved to leaderboard.json and all "
                    "candidate ranks have been recalculated."
                )

            st.dataframe(results_df.style.apply(_highlight_result, axis=1), width="stretch")

            csv_bytes = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Comparison Report (CSV)", csv_bytes, "comparison_report.csv", "text/csv",
                key="download_comparison",
            )

    if not OCR_AVAILABLE or not PDF_AVAILABLE:
        st.info(
            "OCR/PDF dependencies are missing.\n\n"
            "Run:\n\npip install pytesseract pymupdf pillow pandas openpyxl\n\n"
            "You must also install Tesseract-OCR separately."
        )
