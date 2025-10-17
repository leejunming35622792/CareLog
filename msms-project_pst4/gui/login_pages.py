import streamlit as st
from app.schedule import ScheduleManager
from gui.login_gui import register
from gui.login_gui import student_login
from gui.login_gui import teacher_login
from gui.login_gui import staff_login
from gui.student_gui import student_launch
from gui.teacher_gui import teacher_launch
from gui.staff_gui import staff_launch

# --------------- Login -----------------
st.set_page_config(layout="wide", page_title="Music School Management System")

def login_page():
    # control which page to go
    if "page" not in st.session_state:
      st.session_state.page = "login"

    if "register_staff" not in st.session_state:
        st.session_state.register_staff = ""

    # check if manager has been activated
    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()

    if st.session_state.get("page") == "login":
        st.balloons()
        
        # Create header
        st.header("Music School Management System")

        # Create sidebar title
        st.sidebar.title("MSMS Login Page")

        # Create sidebar menu option
        option = st.sidebar.selectbox("Select", ["Register Account", "Student Login", "Teacher Login", "Staff Login"])

        if option == "Register Account":
            register(st.session_state.manager)
        elif option == "Student Login":
            student_login(st.session_state.manager)
        elif option == "Teacher Login":
            teacher_login(st.session_state.manager)
        elif option == "Staff Login":
            staff_login(st.session_state.manager)

    # Direct to user page after logging in
    elif st.session_state.page == "student":
        student_launch(st.session_state.manager, st.session_state.username)

    # Direct to user page after logging in
    elif st.session_state.page == "teacher":
        teacher_launch(st.session_state.manager, st.session_state.username)

    # Direct to user page after logging in
    elif st.session_state.page == "staff":
        staff_launch()
# ---------------------------------------