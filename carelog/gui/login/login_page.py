import streamlit as st
from app.schedule import ScheduleManager
from gui.login.log_in import log_in
from gui.login.register import register
from gui.login.about_us import about_us
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
        st.title("CareLog")

        # Sidebar
        st.sidebar.title("Login")
        option = st.sidebar.selectbox("Select", ["Log In", "Create Account", "About Us"])

        # Logic
        if option == "Log In":
            log_in(st.session_state.manager)
        elif option == "Create Account":
            register(st.session_state.manager)
        elif option == "About Us":
            about_us(st.session_state.manager)

    elif st.session_state.page == "patient":
        patient_page(st.session_state.manager)
    
    elif st.session_state.page == "doctor":
        doctor_page(st.session_state.manager)

    elif st.session_state.page == "nurse":
        nurse_page()

    elif st.session_state.page == "receptionist":
        receptionist_page(st.session_state.manager)

    elif st.session_state.page == "admin":
        admin_page(st.session_state.manager)