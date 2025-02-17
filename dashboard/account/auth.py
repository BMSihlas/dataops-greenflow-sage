import streamlit as st
from components.api_utils import authenticate_user
from streamlit_js_eval import streamlit_js_eval
import time

JWT_TOKEN_SESSION_KEY = "jwt_token"
JWT_LOCAL_STORAGE_KEY  = "jwt_token"
USERNAME_SESSION_KEY = "username"
EXPIRY_LOCAL_STORAGE_KEY = "expiry_time"
TTL_MINUTES = 24 * 59  # ~24 hours - 24 minutes

def login():
    """Login form and authentication logic."""
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        ""
    with col2:
        st.container(height=110, border=False)
        with st.container():
            st.title("Welcome to GreenFlow Sage! 👋")
            st.write("Please sign-in to your account and start the adventure")
            # Username and password input fields
            usernameInpt = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Sign in"):
                user = authenticate_user(usernameInpt, password)
                
                if user and user.token and user.username:
                    # Store token & username in session state
                    st.session_state[JWT_TOKEN_SESSION_KEY] = user.token
                    st.session_state[USERNAME_SESSION_KEY] = user.username
                    st.session_state["logged_in"] = True
                    expiry_time = int(time.time()) + (TTL_MINUTES * 60)
                    st.session_state[EXPIRY_LOCAL_STORAGE_KEY] = expiry_time

                    # Store token in local storage
                    streamlit_js_eval(js_expressions=f"localStorage.setItem('{JWT_LOCAL_STORAGE_KEY}', '{user.token}');", key="set_token")

                    # time.sleep(0.3)

                    streamlit_js_eval(js_expressions=f"localStorage.setItem('username', '{user.username}');", key="set_username")

                    # time.sleep(0.3)

                    streamlit_js_eval(js_expressions=f"localStorage.setItem('{EXPIRY_LOCAL_STORAGE_KEY}', '{expiry_time}');", key="set_expiry")

                    # time.sleep(0.3)

                    st.success(f"✅ Logged in as {user.username}")
                    st.query_params.from_dict({"home": "true"})
                    st.rerun()  # Refresh UI to show dashboard
                else:
                    st.error("❌ Invalid credentials. Try again.")

            st.html(f"<div style='margin-top: 20px;width:100%;align-content:center;text-align:center;'>Copyright © GreenFlow 2025</div>")

def logout():
    """Logout function: clears session and returns to login page."""
    for key in [JWT_TOKEN_SESSION_KEY, USERNAME_SESSION_KEY, "logged_in"]:
        st.session_state.pop(key, None)

    # Remove token from local storage
    streamlit_js_eval(js_expressions=f"localStorage.clear();", key="clear_local_storage")

    time.sleep(0.3)

    st.success("👋 Logged out successfully. Redirecting...")
    st.query_params.from_dict({"logout": "true"})
    st.rerun()

def is_token_valid():
    """Check if stored token is still valid based on expiry time."""
    expiry_timestamp = streamlit_js_eval(js_expressions=f"localStorage.getItem('{EXPIRY_LOCAL_STORAGE_KEY}')", key="get_expiry")

    time.sleep(0.5)

    # Ensure expiry_timestamp is not None and is a valid number
    if expiry_timestamp:
        try:
            expiry_timestamp = int(expiry_timestamp)  # Convert safely
            current_time = int(time.time())
            return current_time < expiry_timestamp
        except ValueError:
            print("Invalid expiry timestamp:", expiry_timestamp)
            return False  # Fallback if conversion fails

    return False
