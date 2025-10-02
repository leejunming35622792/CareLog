import streamlit as st
from app.schedule import ScheduleManager
from gui.login.register import create_account
from gui.login.log_in import log_in
from gui.patients.patient_page import patient_page
from gui.doctors.doctor_page import doctor_page
from gui.nurses.nurse_page import nurse_page
from gui.receptionists.receptionist_page import receptionist_page
from gui.admins.admin_page import admin_page

st.set_page_config(layout="wide")

def login_page():
    # --- Session States ---
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    if "username" not in st.session_state:
        st.session_state.username = ""

    # --- Variables ---


    # --- Default Display ---
    if st.session_state.get("page") == "login":
        # Page Design
        # st.balloons()

        # Sidebar
        st.sidebar.title("CareLog Login")
        option = st.sidebar.selectbox("Select", ["Create Account", "Log In"])

        # Logic
        if option == "Create Account":
            create_account(st.session_state.manager)
    
        elif option == "Log In":
            log_in(st.session_state.manager)

    elif st.session_state.page == "patient":
        patient_page(st.session_state.manager)
    
    elif st.session_state.page == "doctor":
        doctor_page(st.session_state.manager)

    elif st.session_state.page == "nurse":
        nurse_page(st.session_state.manager)

    elif st.session_state.page == "receptionist":
        receptionist_page(st.session_state.manager)

    elif st.session_state.page == "admin":
        admin_page(st.session_state.manager)