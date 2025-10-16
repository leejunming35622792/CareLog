import streamlit as st
import time

def log_in(manager):
    # Variable
    user_list = ["Patient", "Doctor", "Nurse", "Receptionist", "Admin"]

    # Page design
    st.title("CareLog")
    col1, col2 = st.columns(2)

    with col1:
        st.image("img/wallpaper.jpg")
    with col2:
        with st.form("register-form"):
            st.subheader("Login")
            user = st.selectbox("Select User: ", user_list)
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
                    from manager.auth_manager import AuthManager
                    am = AuthManager(manager) # Pass in schedule manager
                    # Add login delay
                    with st.spinner("Logging In..."):
                        time.sleep(2)

                    success, message, user_obj = am.check_credentials(user, username, password)
                    user = user.lower()

                    if success:
                        st.session_state.username = username
                        st.session_state.user = user_obj
                        st.session_state.page = user
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)