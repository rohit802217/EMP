"""
Visual styling: custom CSS (layered on top of .streamlit/config.toml's
native theme) and the letterhead-style hero banner shown at the top
of the app.
"""

import streamlit as st

_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');

.hero-banner {
    background: #16233A;
    border: 1px solid #2A3B58;
    border-top: 4px solid #C9A227;
    border-radius: 4px;
    padding: 28px 36px;
    margin-bottom: 28px;
}
.hero-banner h1 {
    font-family: 'Playfair Display', serif;
    color: #EDEFF3;
    font-size: 2.1rem;
    margin: 0 0 6px 0;
    font-weight: 700;
}
.hero-banner p {
    color: #9FB0C7;
    margin: 0;
    font-size: 0.98rem;
}

h2, h3 {
    font-family: 'Playfair Display', serif;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #C9A227 !important;
}
</style>
"""


def apply_styles():
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


def render_hero_banner():
    st.markdown(
        """
        <div class="hero-banner">
            <h1>📝 6-Paper OMR Evaluation & Result Portal</h1>
            <p>Multi-format answer-sheet evaluation, qualifying checks, merit ranking, and direct results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
