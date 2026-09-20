
import streamlit as st

from config import PAGE_TITLE, PAGE_ICON

from ui.styles import apply_styles, render_hero_banner
from utils.auth import render_admin_login_sidebar, is_admin, admin_only_notice
from ui.leaderboard_page import render_leaderboard_page
from ui.six_paper_page import render_six_paper_page
from ui.vacancy_page import render_vacancy_page
from ui.result_lookup_page import render_result_lookup_page

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)


# =========================================================
# GLOBAL STYLING
# =========================================================

apply_styles()

render_hero_banner()


# =========================================================
# ADMIN LOGIN
# =========================================================
# IMPORTANT:
# This is the ONLY place where admin login is rendered.

render_admin_login_sidebar()


# =========================================================
# MAIN TABS
# =========================================================

tab_labels = ["🔍 Direct Result Lookup", "🧑‍🏫 Teacher Upload & Evaluation", "🏆 Live Leaderboard", "📢 Vacancy"]

tabs = st.tabs(tab_labels)


# =========================================================
# CHECK MY RESULT
# =========================================================

with tabs[0]:
    render_result_lookup_page()


# =========================================================
# LEADERBOARD
# =========================================================

with tabs[1]:
    if is_admin():
        render_six_paper_page()
    else:
        admin_only_notice()


# =========================================================
# VACANCY
# =========================================================

with tabs[2]:
    render_leaderboard_page()


# =========================================================
# SIGN UP
# =========================================================

with tabs[3]:
    render_vacancy_page()
