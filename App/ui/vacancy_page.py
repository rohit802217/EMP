import streamlit as st

from services.vacancy_service import load_vacancies, save_vacancies
from utils.auth import is_admin


def render_vacancy_page():
    st.subheader("📢 Vacancy Listings")

    if is_admin():
        with st.expander("➕ Add New Vacancy"):
            with st.form("vacancy_form", clear_on_submit=True):
                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    job_title = st.text_input("Job Title / Post Name")
                    department = st.text_input("Department / Organization")
                    total_posts = st.number_input("Total Posts", min_value=0, step=1)
                with v_col2:
                    deadline = st.date_input("Application Deadline")
                    qualification = st.text_input("Minimum Qualification")
                    apply_link = st.text_input("Apply Link (URL)")

                vacancy_submitted = st.form_submit_button("Add Vacancy")

            if vacancy_submitted:
                if not job_title.strip():
                    st.error("Job Title is required.")
                else:
                    vacancies = load_vacancies()
                    vacancies.append({
                        "job_title": job_title.strip(),
                        "department": department.strip(),
                        "total_posts": total_posts,
                        "deadline": str(deadline),
                        "qualification": qualification.strip(),
                        "apply_link": apply_link.strip(),
                    })
                    save_vacancies(vacancies)
                    st.success(f"Added vacancy: {job_title}")
                    st.rerun()

    st.markdown("---")
    vacancies = load_vacancies()

    if not vacancies:
        st.info("No vacancies posted yet." + (" Use 'Add New Vacancy' above." if is_admin() else ""))
        return

    for idx, v in enumerate(vacancies):
        with st.container(border=True):
            vc1, vc2 = st.columns([4, 1])
            with vc1:
                st.markdown(f"### {v.get('job_title', 'Untitled')}")
                st.write(f"**Department:** {v.get('department', '—')}")
                st.write(f"**Total Posts:** {v.get('total_posts', '—')}")
                st.write(f"**Minimum Qualification:** {v.get('qualification', '—')}")
                st.write(f"**Deadline:** {v.get('deadline', '—')}")
                if v.get("apply_link"):
                    st.markdown(f"[🔗 Apply Here]({v['apply_link']})")
            with vc2:
                if is_admin() and st.button("🗑️ Delete", key=f"delete_vacancy_{idx}"):
                    vacancies.pop(idx)
                    save_vacancies(vacancies)
                    st.rerun()
