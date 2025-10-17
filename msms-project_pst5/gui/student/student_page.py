import streamlit as st
import pandas as pd
import logging
from app.admin_utils import init_logger, backup_data
from app.schedule import ScheduleManager
from gui.student.s_dashboard import dashboard
from gui.student.s_profile import profile
from gui.student.s_course import course_detail
from gui.student.s_attendance import attendance
from gui.student.s_feedback import feedback
from gui.student.s_student_card import student_card
from gui.student.s_payment import payment

# --- Main Section---
def student_launch(Manager):
    # Session states
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    if "backup" in st.session_state:
        st.session_state.backup = ""
        backup_data()

    if "start_log" not in st.session_state and st.session_state != "":
        st.session_state.start_log = "Logs started"
        init_logger(st.session_state.username)

    # Variables
    global username
    username = st.session_state.username
    global manager
    manager = st.session_state.manager
    global current_student
    current_student = next((s for s in manager.students if s.username == username), None)
    global current_course
    current_course = next((s.enrolled_course_ids for s in manager.students if s.username == username), None)

    # Page design
    st.sidebar.title("MSMS Navigation")
    st.sidebar.write(f"@{st.session_state.username}")
    st.sidebar.divider()
    st.title("Music School Management System")

    # Menu
    page = st.sidebar.radio("Go to", ["Dashboard", "Personal", "Courses", "Attendance", "Payment", "Student Card", "Feedback"])

    st.sidebar.divider()
    st.sidebar.button("Logout", on_click=logout)

    if page == "Dashboard":
        dashboard()
    elif page == "Personal":
        profile()
    elif page == "Courses":
        course_detail()
    elif page == "Attendance":
        attendance()
    elif page == "Payment":
        payment()
    elif page == "Student Card":
        student_card()
    elif page == "Feedback":
        feedback()

    logging.info(f"{page}")

# --- Sub-section: Logout ---
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True
    logging.info("Successfully Logout")