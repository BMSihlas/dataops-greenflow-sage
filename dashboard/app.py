import os
import streamlit as st
from account.auth import login, logout, is_token_valid, JWT_LOCAL_STORAGE_KEY, JWT_TOKEN_SESSION_KEY, USERNAME_SESSION_KEY
from reports.home import authenticated_home
from reports.dashboard import dashboard
from reports.sectors import sector
from streamlit_js_eval import streamlit_js_eval
import time

# Set page configuration
st.set_page_config(page_title="GreenFlow Sage", layout="wide")

# Check if user is logged in
if JWT_TOKEN_SESSION_KEY not in st.session_state:
    stored_token = streamlit_js_eval(js_expressions=f"localStorage.getItem('{JWT_LOCAL_STORAGE_KEY}')", key="get_token")

    stored_username = streamlit_js_eval(js_expressions=f"localStorage.getItem('{USERNAME_SESSION_KEY}')", key="get_username")

    time.sleep(0.3)
    
    if stored_token is not None and stored_username is not None:
        if is_token_valid():
            st.session_state.update({
                JWT_TOKEN_SESSION_KEY: stored_token,
                USERNAME_SESSION_KEY: stored_username,
                "logged_in": True
            })
            if "first_rerun" not in st.session_state:
                st.session_state["first_rerun"] = True
                st.query_params.from_dict({"home": "true"})
                st.rerun()
        else:
            logout()

time.sleep(0.5)

image_path = os.path.join("dashboard", "assets", "greenflow_logo.png")
st.logo(image_path, icon_image=image_path, size="large")

if st.session_state.get("logged_in"):
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    home_page = st.Page(authenticated_home, title="Home", icon=":material/home:")
    dashboard_page = st.Page(dashboard, title="Global", icon=":material/dashboard:")
    sectors_page = st.Page(sector, title="Sectors", icon=":material/maps_home_work:")
    sage_structure = {
        "GREENFLOW - SAGE": [
            home_page,
            dashboard_page,
            sectors_page,
        ],
    }

    navigation_structure = {"Account": [logout_page]}
    pg = st.navigation(sage_structure | navigation_structure)

    st.sidebar.subheader("Created by")
    st.sidebar.markdown(
        """
        **Bruno Matos**  
        Fullstack Developer & Software Engineer  
        Passionate about Programming, Data, and Sustainable Tech.  
        [🔗 GitHub](https://github.com/BMSihlas) | [📧 Contact](mailto:bruno.rosal.matos@gmail.com)
        """
    )

else:
    pg = st.navigation([st.Page(login)])

pg.run()