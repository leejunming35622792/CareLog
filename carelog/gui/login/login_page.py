import streamlit as st
from app.schedule import ScheduleManager
from gui.login.register import create_account

st.set_page_config(layout="wide", page_title="CareLog")

def login_page():
    # --- Session States ---
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    # --- Variables ---
    tabs = ["Create Account", "Log In"]

    # --- Default Display ---
    if st.session_state.get("page") == "login":
        # Page Design
        st.balloons()
        st.title("CareLog")

        # Sidebar
        st.sidebar.title("CareLog Login")
        option = st.sidebar("Select", tabs)

        # Logic
        if option == "Create Account":
            create_account(st.session_state.manager)
        elif option == "Log In":
            pass

    elif st.session_state.page == "patients":
        patient_page(st.session_state.manager, st.session_state.username)

    elif st.session_state.page == "doctors":
        ...

    elif st.session_state.page == "nurses":
        ...

    elif st.session_state.page == "receptionist":
        ...

    elif st.session_state.page == "admin":
        ...
