import streamlit as st
import time

def register_page(manager):
    manager = st.session_state.manager

    if "detail" not in st.session_state:
        st.session_state.detail = "pending"

    if st.session_state.detail == "pending":
        register(manager)
    elif st.session_state.detail == "required":
        if st.session_state.staff == "Student":
            enter_student_details(manager)
        elif st.session_state.staff == "Teacher":
            enter_teacher_detail(manager)

def enter_student_details(manager):
    with st.form("enter-detail-form"):
        st.info("You are almost there...!")
        # Get name, instrument
        name = st.text_input("Name: ")
        instrument = st.text_input("Instrument: ")
        
        # Get courses
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        if course_disp:
            course_list = st.multiselect("Select:", course_disp.keys())
            enrolled_course = [course_disp[c] for c in course_list]
        else:
            course_list = st.multiselect("Select:", "No course found")
            enrolled_course = []

        # Button
        continue_button = st.form_submit_button("Continue")

        if continue_button:
            errors = []

            if not name:
                errors.append("Please enter a name!")
            if not enrolled_course:
                enrolled_course = []
            if errors:
                for e in errors:
                    st.error(e)
            else:
                name = name.title()
                instrument = instrument.title()
                username = st.session_state.username
                password = st.session_state.password
                result = manager.add_student(name, username, password, instrument, enrolled_course)
                st.session_state.page = "student"
                with st.spinner("Creating account"):
                    time.sleep(1.5)
                    manager.save()
                st.rerun()
        
def enter_teacher_detail(manager):
    with st.form("enter-teacher-detail-form"):
        # Get name, instrument
        name = st.text_input("Name: ")
        speciality = st.text_input("Speciality: ")

        # Button
        continue_button = st.form_submit_button("Continue")

        if continue_button:
            errors = []

            if not name:
                errors.append("Please enter a name!")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                
                name = name.upper()
                speciality = speciality.upper()
                username = st.session_state.username
                password = st.session_state.password
                result = manager.add_teacher(name, username, password, speciality)
                st.session_state.page = "teacher"
                with st.spinner("Creating account"):
                    time.sleep(1.5)
                    manager.save()
                st.rerun()

def register(manager):
    manager = st.session_state.manager
    st.header("Music School Management System (MSMS.v5)")
    st.info("Welcome! To register a new account, please enter an username and password")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("register-form"):
            st.subheader("Register Account")

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
                    st.session_state.staff = staff
                    st.session_state.username = username
                    st.session_state.password = password
                    st.session_state.detail = "required"
                    st.rerun()              

    with col2:
        st.image("img/img1.jpg")
