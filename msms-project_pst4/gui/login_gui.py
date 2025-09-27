import streamlit as st
import time
from gui.main_dashboard import launch
from gui.student_gui import student_launch
from app.schedule import ScheduleManager

st.balloons()

def register(manager):  
    with st.form("register-form"):
        st.subheader("Register Account")
        st.info("Welcome! To register a new account, please choose an username and password")

        # Create Input Box
        staff = st.selectbox("Are you a student or teacher?", ["Student", "Teacher"])
        username = st.text_input("Enter New Username: ", key="input_username")
        password = st.text_input("Enter New Password: ", key="input_password",type="password")
        again_password = st.text_input("Enter Password Again: ", key="input_again_password",type="password")
        register_button = st.form_submit_button("Create New Account")

        if register_button:
            errors = []
            if not username:
                errors.append("Username cannot be empty!")
            if not password:
                errors.append("Password cannot be empty!")
            if " " in username:
                errors.append("Username cannot contain spaces!")
            if password != again_password:
                errors.append("Password does not match!")
            if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                errors.append("Username has been taken")
            
            if errors:
                for e in errors:
                    st.error(e)

            else:                        
                if staff == "Student":
                    result = manager.enrolment("s", username, password, None, "", [])
                    st.session_state.register_staff = "Student"
                    st.session_state.page = "student"
                elif staff == "Teacher":
                    result = manager.enrolment("t", username, password, None, "", "")
                    st.session_state.register_staff = "Teacher"
                    st.session_state.page = "teacher"

                if result:
                    manager.save()
                    st.toast("Successfully registered!")
                    st.session_state.username = username
                    st.rerun()

def student_login(manager):
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    with st.form("student-login-form"):
        st.subheader("Student Login")
        credentials = [{u.username: u.password} for u in manager.students]
        all_username = [u.username for u in manager.students]

        username = st.text_input("Enter Username: ")
        password = st.text_input("Enter Password: ", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            errors = []

            # Empty field validation
            if not username:
                errors.append("Username cannot be empty!")
            if not password:
                errors.append("Password cannot be empty!")

            # If any validation errors, show them and stop
            if errors:
                for e in errors:
                    st.error(e)
                st.stop()  # prevent further execution

            # Check if username exists
            if username not in all_username:
                st.error("Incorrect username and password!")
                st.stop()

            # Convert credentials list into a dict {username: password}
            creds_dict = {list(c.keys())[0]: list(c.values())[0] for c in credentials}

            # Verify password
            if creds_dict.get(username) == password:
                with st.spinner("Logging in..."):
                    time.sleep(1)
                st.success("Login successfully!")
                st.session_state.page = "student"
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Incorrect password!")

def teacher_login(manager):
    with st.form("teacher-login-form"):
        st.subheader("Teacher Login")
        credentials = [{t.username: t.password} for t in manager.teachers]
        all_username = [s.username for s in manager.teachers]

        username = st.text_input("Enter Username: ")
        password = st.text_input("Enter Password: ", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            errors = []

            if not username:
                errors.append("Username cannot be empty!")
            if not password:
                errors.append("Password cannot be empty!")
            if username not in all_username:
                st.error("Incorrect username and password!")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                for c in credentials:
                    if c.get(username) == password:
                        st.success("Login successfully!")
                        with st.spinner("Login in...", show_time=True):
                            time.sleep(1)
                        st.session_state.page = "teacher"
                        st.session_state.username = username
                        st.rerun()

def staff_login(manager):
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    with st.form("staff-login-form"):
        st.subheader("Staff Login")
        credentials = [{u.username: u.password} for u in manager.staff]
        all_username = [u.username for u in manager.staff]

        username = st.text_input("Enter Username: ")
        password = st.text_input("Enter Password: ",type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            errors = []

            if username not in all_username:
                st.error("Incorrect username and password!")
            else:
                for c in credentials:
                    if c.get(username) == password:
                        with st.spinner("Login in...", show_time=True):
                            time.sleep(1)
                            st.toast("Login successfully!")
                        st.session_state.page = "staff"
                        st.session_state.username = username
                        st.rerun()
                st.error("Incorrect password!") 
