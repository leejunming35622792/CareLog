import streamlit as st
import datetime
from app.nurse import NurseUser
from helper_manager.appointment_manager import AppointmentManager
from gui.nurses.nurse_dashboard import dashboard
from gui.nurses.nurse_profile import profile_page
from gui.nurses.nurse_appt_page import appointments_page
from gui.nurses.nurse_records import patient_records_page
from gui.nurses.nurse_remark import remarks_page
from gui.nurses.nurse_shift import shift_page

appt_manager = AppointmentManager(st.session_state.manager)

def nurse_page(nurse: NurseUser):
    global username
    username = st.session_state.username
    global manager
    manager = st.session_state.manager

    if not username:
        st.error("No user logged in")
        return

    tabs = ["Dashboard", "Profile", "Patient", "Appointments", "Shift", "Remarks"]

    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    st.sidebar.divider()
    option = st.sidebar.radio("Select", tabs, key="nurse_sidebar_radio")
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True, key="nurse_logout_btn")
    
    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient":
        patient_records_page(manager, username)
    elif option == "Appointments":
        appointments_page(manager, username)
    elif option == "Shift":
        shift_page()
    elif option == "Remarks":
        remarks_page(manager, username)

    if "success_msg" in st.session_state and st.session_state.success_msg != "":
        st.success(st.session_state.success_msg)
        st.session_state.success_msg = ""

    # End of Page
    st.divider()
    st.markdown("<h6 style='text-align:center'>CareLog</h6>", unsafe_allow_html=True)
    
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True