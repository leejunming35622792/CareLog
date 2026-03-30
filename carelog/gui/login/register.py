import streamlit as st
import app.utils as utils
from gui.login.get_detail import get_detail
from app.user import User
#handles user registration for the application, managinga two phase process: basic info and detailed info
def register(manager):
    if "register_phase" not in st.session_state:
        st.session_state.register_phase = "basic"

    if st.session_state.register_phase == "details":
        get_detail(
            st.session_state.role,
            st.session_state.username_temp,
            st.session_state.password_temp,
            st.session_state.user_id_temp
        )

    else:
        # registration with basic info 
        st.title("CareLog")
        col1, col2 = st.columns(2)
        with col1:
            # basic info form 
            if st.session_state.register_phase == "basic":
                with st.form("register-form"):
                    st.subheader("Create Account")

                    role = st.selectbox("Select User:", ["Patient", "Doctor", "Nurse", "Receptionist"])
                    user_id = User.get_next_id(manager, role)

                    username = st.text_input("Username:")
                    password = st.text_input("Password:", type="password")

                    confirm_pw = st.text_input("Confirm Password:", type="password", help="Password confirmation")

                    submit = st.form_submit_button("Register")

                    if submit:
                        errors = []

                        if not username:
                            errors.append("Username cannot be empty")

                        # username check for duplicate to determine uniqueness
                        all_usernames = [u.username for group in [
                            manager.patients,
                            manager.doctors,
                            manager.nurses,
                            manager.receptionists,
                            manager.admins
                        ] for u in group]
                                
                        if username in all_usernames:
                            errors.append("Username already in used")
                        
                        # validate password
                        if not password:
                            errors.append("Password cannot be empty")
                        elif confirm_pw:
                            if len(password) < 8:
                                errors.append("Password must be at least 8 characters")
                            if not any(c.isupper() for c in password):
                                errors.append("Password must contain at least one uppercase letter")
                            if not any(c.isdigit() for c in password):
                                errors.append("Password must contain at least one number")
                        elif password != confirm_pw:
                            errors.append("Password not match")
                        
                            
                        if errors:
                            for e in errors:
                                st.error(e)
                        else:
                            st.session_state.role = role
                            st.session_state.username_temp = username
                            st.session_state.password_temp = password
                            st.session_state.user_id_temp = user_id
                            st.session_state.register_phase = "details"
                            st.rerun()
        
        with col2:
            st.image("img/wallpaper.jpg", use_container_width=True)
