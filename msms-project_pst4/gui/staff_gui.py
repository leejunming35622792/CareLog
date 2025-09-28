# gui/main_dashboard.py
import streamlit as st
from app.schedule import ScheduleManager
from gui.staff.dashboard import dashboard
from gui.staff.student_pages import show_student_management_page
from gui.staff.teacher_pages import show_teacher_management_page
from gui.staff.course_pages import show_course_management_page
from gui.staff.roster_pages import show_roster_page
from gui.staff.printcard_pages import show_print_student_card_page
from gui.staff.payment_pages import show_payment_page
from gui.staff.display_pages import display_all_page

def staff_launch():
    st.set_page_config(layout="wide", page_title="Music School Management System")

    # Gets all features from ScheduleManager()
    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()

    # Logout back to Login Page
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    st.sidebar.title("MSMS Navigation")

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
        st.header("Payments")
        st.warning("This feature will be implemented in PST5.")
        show_payment_page(st.session_state.manager)
    elif page == "Data Management":
        display_all_page(st.session_state.manager)

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True