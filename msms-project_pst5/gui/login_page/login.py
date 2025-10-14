import streamlit as st

def login(manager):
    # Variables
    manager = st.session_state.manager

    # Page design
    st.header("Music School Management System (MSMS.v5)")
    st.info("Welcome! We are happy you are back!")
    col1, col2 = st.columns(2)

    with col1:
        st.image('img/img1.jpg')

    with col2:
        with st.form("login-form"):
            st.subheader("Login Account")
            user = st.selectbox("Select:", ["Student", "Teacher", "Staff"])
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            submit = st.form_submit_button("Log In")

            if submit:
                errors = []

                if not username:
                    errors.append("Please enter username!")
                if not password:
                    errors.append("Please enter password!")

                if errors:
                    for e in errors:
                        st.error(e)
                    st.stop()
                else:
                    result = manager.login(user, username, password)

                    if not result:
                        st.error("Username and password do not match!")
                        st.stop()
                
                if result == "Student":
                    st.session_state.page = "student"
                elif result == "Teacher":
                    st.session_state.page = "teacher"
                elif result == "Staff":
                    st.session_state.page = "staff"
                
                st.session_state.username = username
                st.rerun()
