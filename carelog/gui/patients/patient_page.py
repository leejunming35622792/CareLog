import streamlit as st
from gui.patients.patient_dashboard import dashboard
from gui.patients.patient_profile import profile
from gui.patients.patient_record import record
from gui.patients.patient_appointment import appointment

def patient_page(manager):
    # Variables
    username = st.session_state.username
    tabs = ["Dashboard", "Profile", "Records", "Appointments"]

    # Session state
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)

    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile(manager, username)
    elif option == "Records":
        record(manager)
    elif option == "Appointments":
        appointment(manager)

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True