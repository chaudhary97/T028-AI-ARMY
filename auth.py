import streamlit as st

# --- USER AUTHENTICATION with ROLES ---
VALID_CREDENTIALS = {
    "admin": ("admin123", "admin"),
    "mentor1": ("pass1", "mentor"),
    "mentor2": ("pass2", "mentor")
}

def check_login(username, password):
    """Checks if the username and password are valid."""
    if username in VALID_CREDENTIALS:
        stored_password, role = VALID_CREDENTIALS[username]
        if password == stored_password:
            return role
    return None

def login_page():
    """Handles the login UI. Only shows the page if the user is not authenticated."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = ""

    # If the user is already authenticated, immediately return True
    # and do not draw the login page.
    if st.session_state.authenticated:
        return True

    # --- If NOT authenticated, draw the login page UI ---
    st.title("🎓 AI-Based Student Dropout Prediction System")
    st.subheader("Please Login to Continue")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            role = check_login(username, password)
            if role:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    # If the code reaches here, the form was displayed but not successfully submitted.
    return False