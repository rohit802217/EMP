
import streamlit as st
from config import ADMIN_PASSWORD


# =========================================================
# ADMIN AUTHENTICATION
# =========================================================

def is_admin():
    return st.session_state.get("is_admin", False)


def render_admin_login_sidebar():
    """Render admin login/logout exactly once."""

    with st.sidebar:
        st.markdown("### 🔐 Admin Access")

        if is_admin():
            st.success("Logged in as Admin")

            if st.button("Log out", key="admin_logout"):
                st.session_state["is_admin"] = False
                st.rerun()

        else:
            password = st.text_input(
                "Admin password",
                type="password",
                key="admin_pwd_input"
            )

            if st.button("Log in", key="admin_login_btn"):
                if password == ADMIN_PASSWORD:
                    st.session_state["is_admin"] = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")


# =========================================================
# USER SIGNUP
# =========================================================

def render_signup():
    """Render user signup separately from admin login."""

    if "users" not in st.session_state:
        st.session_state["users"] = {}

    st.markdown("## 📝 Create Account")

    username = st.text_input(
        "Username",
        key="signup_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="signup_confirm_password"
    )

    if st.button("Create Account", key="create_account_btn"):

        users = st.session_state["users"]

        if not username or not password or not confirm_password:
            st.warning("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif username in users:
            st.error("Username already exists.")

        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")

        else:
            users[username] = password
            st.session_state["users"] = users

            st.success(
                f"Account '{username}' created successfully!"
            )


# =========================================================
# ADMIN-ONLY CHECK
# =========================================================

def admin_only_notice():

    if not is_admin():
        st.warning("🔐 Admin access required.")
        return False

    return True

