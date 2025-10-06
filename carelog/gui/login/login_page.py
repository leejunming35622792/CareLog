import streamlit as st
from app.schedule import ScheduleManager

st.set_page_config(layout="wide")

def login_page():
    # --- Session States ---
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    if "username" not in st.session_state:
        st.session_state.username = ""

    # --- Default Display ---
    if st.session_state.get("page") == "login":
        # Page Design
        st.title("CareLog")

        # Sidebar
        st.sidebar.title("Login")
        option = st.sidebar.selectbox("Select", ["Log In", "Create Account", "About Us"])

        # Logic
        if option == "Log In":
            from gui.login.log_in import log_in
            log_in(st.session_state.manager)
        elif option == "Create Account":
            from gui.login.register import register
            register(st.session_state.manager)
        elif option == "About Us":
            from gui.login.about_us import about_us
            about_us(st.session_state.manager)

    elif st.session_state.page == "patient":
        from gui.patients.patient_page import patient_page
        patient_page(st.session_state.manager)
    
    elif st.session_state.page == "doctor":
        from gui.doctors.doctor_page import doctor_page
        doctor_page(st.session_state.manager)

    elif st.session_state.page == "nurse":
        from gui.nurses.nurse_page import nurse_page
        nurse_page(st.session_state.manager)

    elif st.session_state.page == "receptionist":
        from gui.receptionists.receptionist_page import receptionist_page
        receptionist_page(st.session_state.manager)

    elif st.session_state.page == "admin":
        from gui.admins.admin_page import admin_page
        admin_page(st.session_state.manager)