import streamlit as st
import time

def log_in(manager):
    # Variable
    user = ["Patient", "Doctor", "Nurse", "Receptionist", "Admin"]

    # Page design
    col1, col2 = st.columns(2)

    with col1:
        st.image("img/wallpaper.jpg")
    with col2:
        with st.form("register-form"):
            st.subheader("Login")
            staff = st.selectbox("User", user)
            username = st.text_input("Username: ", placeholder="")
            password = st.text_input("Password: ", placeholder="", type="password")
            button = st.form_submit_button("Login")

            if button:
                # Variables
                errors = []
                
                if not username:
                    errors.append("Username cannot be empty!")
                if not password:
                    errors.append("Password cannot be empty!")
                
                if errors:
                    for e in errors:
                        st.error(e)
                    st.stop()
                else:
                    # Add login delay
                    with st.spinner("Logging In..."):
                        time.sleep(2)

                    role = manager.check_credentials(staff, username, password)

                    if role == "Patient" :
                        st.session_state.page = "patient"
                        st.session_state.username = username
                    elif role == "Doctor":
                        st.session_state.page = "doctor"
                        st.session_state.username = username
                    elif role == "Nurse":
                        st.session_state.page = "nurse"
                        st.session_state.username = username
                    elif role == "Receptionist":
                        st.session_state.page = "receptionist"
                        st.session_state.username = username
                    elif role == "Admin":
                        st.session_state.page = "admin"
                        st.session_state.username = username
                    else:
                        st.error("Username and password do not match!")
                        st.stop()
                    st.rerun()