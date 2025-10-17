import streamlit as st
import time

# ===========================
# REGISTER PAGE CONTROLLER
# ===========================
def register_page(manager):
    # Access manager object from Streamlit session
    manager = st.session_state.manager

    # Initialize session variable for multi-step registration flow
    if "detail" not in st.session_state:
        st.session_state.detail = "pending"

    # Step 1: Register basic info
    if st.session_state.detail == "pending":
        register(manager)
    # Step 2: Enter more details based on role
    elif st.session_state.detail == "required":
        if st.session_state.staff == "Student":
            enter_student_details(manager)
        elif st.session_state.staff == "Teacher":
            enter_teacher_detail(manager)


# ===========================
# STUDENT DETAIL ENTRY
# ===========================
def enter_student_details(manager):
    # Create a form for student detail input
    with st.form("enter-detail-form"):
        st.info("You are almost there...!")

        # Basic inputs
        name = st.text_input("Name: ")
        instrument = st.text_input("Instrument: ")
        
        # Build a dictionary: display text → course ID
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}

        # If there are existing courses, display them in a multiselect
        if course_disp:
            course_list = st.multiselect("Select:", course_disp.keys())
            enrolled_course = [course_disp[c] for c in course_list]
        else:
            # Handle case when no courses exist
            course_list = st.multiselect("Select:", ["No course found"])
            enrolled_course = []

        # Submit button for this form
        continue_button = st.form_submit_button("Continue")

        # When button is clicked
        if continue_button:
            errors = []

            # Validation checks
            if not name:
                errors.append("Please enter a name!")
            if not enrolled_course:
                enrolled_course = []

            # Display all collected errors (if any)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Proper capitalization for uniformity
                name = name.title()
                instrument = instrument.title()

                # Retrieve credentials from previous form
                username = st.session_state.username
                password = st.session_state.password

                # Register the new student using manager
                result = manager.add_student(name, username, password, instrument, enrolled_course)

                # Set page to student dashboard
                st.session_state.page = "student"

                # Show spinner to simulate data saving delay
                with st.spinner("Creating account"):
                    time.sleep(1.5)
                    manager.save()

                # Refresh page to load student interface
                st.rerun()
        

# ===========================
# TEACHER DETAIL ENTRY
# ===========================
def enter_teacher_detail(manager):
    # Create a form for teacher detail input
    with st.form("enter-teacher-detail-form"):
        # Input fields
        name = st.text_input("Name: ")
        speciality = st.text_input("Speciality: ")

        # Submit button
        continue_button = st.form_submit_button("Continue")

        # When button clicked
        if continue_button:
            errors = []

            # Validation
            if not name:
                errors.append("Please enter a name!")

            # Display validation errors
            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Standardize text format (uppercase)
                name = name.upper()
                speciality = speciality.upper()

                # Retrieve credentials from session
                username = st.session_state.username
                password = st.session_state.password

                # Add teacher record
                result = manager.add_teacher(name, username, password, speciality)

                # Move user to teacher dashboard
                st.session_state.page = "teacher"

                # Save and show loading animation
                with st.spinner("Creating account"):
                    time.sleep(1.5)
                    manager.save()

                # Refresh Streamlit session
                st.rerun()


# ===========================
# ACCOUNT REGISTRATION PAGE
# ===========================
def register(manager):
    # Access manager from session
    manager = st.session_state.manager

    # Page title and instructions
    st.header("Music School Management System (MSMS.v5)")
    st.info("Welcome! To register a new account, please enter an username and password")

    # Create two columns: form (left) + image (right)
    col1, col2 = st.columns(2)
    
    # ----- LEFT COLUMN: Registration Form -----
    with col1:
        with st.form("register-form"):
            st.subheader("Register Account")

            # Account type selector
            staff = st.selectbox("Are you a student or teacher?", ["Student", "Teacher"])
            
            # Credentials input fields
            username = st.text_input("Enter New Username: ", key="input_username")
            password = st.text_input("Enter New Password: ", key="input_password", type="password")
            again_password = st.text_input("Enter Password Again: ", key="input_again_password", type="password")
            
            # Submit button
            register_button = st.form_submit_button("Create New Account")

            # When button is clicked
            if register_button:
                errors = []

                # Basic validations
                if not username:
                    errors.append("Username cannot be empty!")
                if not password:
                    errors.append("Password cannot be empty!")
                if " " in username:
                    errors.append("Username cannot contain spaces!")
                if password != again_password:
                    errors.append("Password does not match!")
                
                # Check if username already exists among students or teachers
                if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                    errors.append("Username has been taken")
                
                # Display errors (if any)
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    # Save form data temporarily into session
                    st.session_state.staff = staff
                    st.session_state.username = username
                    st.session_state.password = password

                    # Move to the next registration phase
                    st.session_state.detail = "required"
                    st.rerun()

    # ----- RIGHT COLUMN: Decorative Image -----
    with col2:
        st.image("img/img1.jpg")
