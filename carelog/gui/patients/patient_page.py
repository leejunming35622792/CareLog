import streamlit as st
from gui.patients.patient_dashboard import dashboard
from gui.patients.patient_profile import profile
from gui.patients.patient_record import record
from gui.patients.patient_appointment import appointment

def patient_page(manager):
    # variables
    username = st.session_state.username
    tabs = ["Dashboard", "Profile", "Records", "Appointments"]

    # session state management
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()
    # initialize session state variables
    if "edit" not in st.session_state:
        st.session_state.edit = ""

    if "cancel" not in st.session_state:
        st.session_state.cancel = ""

    if "option" not in st.session_state:
        st.session_state.option = ""

    if st.session_state.option != "Dashboard":
        del st.session_state.success_msg
        st.session_state.success_msg = []

    # page layout design
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    st.sidebar.divider()
    option = st.sidebar.radio("Select", tabs)
    st.session_state.option = option
    st.sidebar.button(
        "🚪 Logout", on_click=logout, use_container_width=True
    )
    # content of the page
    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile(manager)
    elif option == "Records":
        record(manager)
    elif option == "Appointments":
        appointment(manager)

    # end of Page
    st.divider()
    st.markdown("<h6 style='text-align:center'>CareLog</h6>", unsafe_allow_html=True)
    
# logout function
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True
    st.session_state.get_user_detail = ""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()