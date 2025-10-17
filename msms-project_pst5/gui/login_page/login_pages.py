import streamlit as st
import logging
from app.schedule import ScheduleManager
from app.admin_utils import init_logger
from gui.login_page.login import login
from gui.login_page.register import register_page
from gui.student.student_page import student_launch
from gui.teacher.teacher_page import teacher_launch

# --------------- Login -----------------
st.set_page_config(layout="wide", page_title="Music School Management System")

def login_page():
    # Session States
    if "page" not in st.session_state:
      st.session_state.page = "login"

    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()

    if "username" not in st.session_state:
        st.session_state.username = ""
    
    if "password" not in st.session_state:
        st.session_state.password = ""

    if "staff" not in st.session_state:
        st.session_state.user = ""

    if st.session_state.get("page") == "login":
        st.balloons()

        # Create sidebar title
        st.sidebar.title("MSMS Login Page")

        # Create sidebar menu option
        option = st.sidebar.selectbox("Select", ["Login", "Register"])

        if option == "Login":
            login(st.session_state.manager)
        elif option == "Register":
            register_page(st.session_state.manager)
        
        print("\nSystem - New user joined the session.")

    # Direct to user page after logging in
    elif st.session_state.page == "student":
        student_launch(st.session_state.manager)

    # Direct to user page after logging in
    elif st.session_state.page == "teacher":
        teacher_launch(st.session_state.manager)

# ---------------------------------------