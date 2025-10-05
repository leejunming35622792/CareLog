import streamlit as st
import time, datetime
import app.utils as utils
from app.user import User

def register(manager):
    # --- Variable ---
    user = User("","","","","","","","")

    # --- Page design ---
    st.title("Register New Account")
    
    col1, col2 = st.columns(2)

    with col1:
        st.image("img/wallpaper.jpg", use_container_width=True)

    with col2:
        with st.form("register_form"):
            st.subheader("Create Account")

            # Select role
            role = st.selectbox("Select Role", ["Patient", "Doctor", "Nurse", "Receptionist"])

            # Generate ID
            user_id = user.get_next_id(role)
            
            # st.text_input("Assigned ID:", value=user_id, disabled=True)

            # Credentials
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Submit
            submit = st.form_submit_button("Register")
            if submit:
                with st.spinner("Processing..."):
                    time.sleep(1)
                success, message, user_obj = user.create_user(role, username, password, user_id, date)

                if success:
                    manager.save()
                    utils.log_event(f"{role} {username} registered successfully.", "INFO")
                    st.success(message)
                    st.toast(f"Welcome, {username}!")
                    st.session_state.page = role.lower()
                    st.rerun()
                else:
                    utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")
                    st.error(message)
