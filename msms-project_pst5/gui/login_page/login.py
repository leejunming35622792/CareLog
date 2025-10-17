import streamlit as st

def login(manager):
    """
    Handles the login page UI and logic for the Music School Management System (MSMS.v5).
    Allows users (Student, Teacher, Staff) to log in through the Streamlit interface.
    """
    # Access the main data manager from session state
    manager = st.session_state.manager

    # ----- Page Layout -----
    st.header("Music School Management System (MSMS.v5)")
    st.info("Welcome! We are happy you are back!")
    col1, col2 = st.columns(2)

    # Left column: display welcome image
    with col1:
        st.image('img/img1.jpg')

    # Right column: login form
    with col2:
        with st.form("login-form"):
            st.subheader("Login Account")

            # Input fields
            user = st.selectbox("Select:", ["Student", "Teacher", "Staff"])
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            submit = st.form_submit_button("Log In")

            if submit:
                # Collect and display validation errors
                errors = []
                if not username:
                    errors.append("Please enter username!")
                if not password:
                    errors.append("Please enter password!")

                # Stop execution if there are input errors
                if errors:
                    for e in errors:
                        st.error(e)
                    st.stop()

                # Authenticate credentials using manager.login()
                result = manager.login(user, username, password)

                if not result:
                    st.error("Username and password do not match!")
                    st.stop()
                
                # Redirect to respective dashboard upon success
                if result == "Student":
                    st.session_state.page = "student"
                elif result == "Teacher":
                    st.session_state.page = "teacher"
                elif result == "Staff":
                    st.session_state.page = "staff"
                
                # Store session details and reload page
                st.session_state.username = username
                st.rerun()
