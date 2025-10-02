import streamlit as st
from gui.patients.patient_dashboard import dashboard
from gui.patients.patient_profile import profile
from app.schedule import ScheduleManager

def patient_page(manager):
    # Variables
    username = st.session_state.username
    tabs = ["Dashboard", "Profile", "Records", "Appointments"]

    # Session state
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.title("CareLog")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)

    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile(manager, username)
    elif option == "Records":
        st.write("This is the Records Page")
    elif option == "Appointments":
        st.write("This is the Appointments Page")

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True