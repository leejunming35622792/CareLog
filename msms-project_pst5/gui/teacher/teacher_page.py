# gui/main_dashboard.py
import streamlit as st
from app.schedule import ScheduleManager
from gui.teacher.t_dashboard import dashboard
from gui.teacher.student_management import show_student_management_page
from gui.teacher.teacher_management import show_teacher_management_page
from gui.teacher.course_pages import show_course_management_page
from gui.teacher.roster_pages import show_roster_page
from gui.teacher.printcard_pages import show_print_student_card_page
from gui.teacher.payment_pages import payment
from gui.teacher.display_pages import display_all_page
from app.admin_utils import init_logger

def teacher_launch(manager):
    st.set_page_config(layout="wide", page_title="Music School Management System")

    # Gets all features from ScheduleManager()
    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()

    # Logout back to Login Page
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    
    if "start_log" not in st.session_state and st.session_state != "":
        st.session_state.start_log = "Logs started"
        init_logger(st.session_state.username)

    st.title("Music School Management System")
    st.sidebar.title("MSMS Navigation")
    st.sidebar.write(f"@{st.session_state.username}")

    # Create a radio button menu in the sidebar for page navigation.
    page = st.sidebar.radio("Go to", ["Dashboard", "Student Management", "Teacher Management", "Course Management","Print Daily Roster", "Print Student Card","Payments (stub)", "Data Management"])

    st.sidebar.button("Logout", on_click=logout)

    # Use an if/elif block to call the correct function to render the selected page.
    if page == "Dashboard":
        dashboard(st.session_state.manager)
    elif page == "Student Management":
        show_student_management_page(st.session_state.manager)
    elif page == "Teacher Management":
        show_teacher_management_page(st.session_state.manager)
    elif page == "Course Management":
        show_course_management_page(st.session_state.manager)
    elif page == "Print Daily Roster":
        show_roster_page(st.session_state.manager)
    elif page == "Print Student Card":
        show_print_student_card_page(st.session_state.manager)
    elif page == "Payments (stub)":
        payment(st.session_state.manager)
    elif page == "Data Management":
        display_all_page(st.session_state.manager)

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True