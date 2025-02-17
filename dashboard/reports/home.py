import os
import streamlit as st
from account.auth import USERNAME_SESSION_KEY

def authenticated_home():
    """Displays user dashboard after successful login."""
    st.header(f"Welcome, **{st.session_state[USERNAME_SESSION_KEY]}**!")