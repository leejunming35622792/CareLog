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

# def create_account(manager):
#     # Variables
#     all_username = [p.username for p in manager.patients] + [d.username for d in manager.doctors] + [n.username for n in manager.nurses] + [r.username for r in manager.receptionists] + [a.username for a in manager.admins]

#     col1, col2 = st.columns(2)

#     with col1:
#         st.image("C:\\Users\\Owner\\FIT1056-Sem2-2025\\carelog\\img\\wallpaper.jpg")

#     with col2:
#         with st.form("register-form"):
#             st.subheader("Create Account")
#             username = st.text_input("Username: ")
#             password = st.text_input("Password: ")
#             button = st.form_submit_button("Create Account")

#             if button:
#                 # Variables
#                 errors = []

#                 if not username:
#                     errors.append("Username cannot be empty!")
#                 else:
#                     if username in all_username:
#                         errors.append("Username has been taken!")
#                 if not password:
#                     errors.append("Password cannot be empty!")
#                 else:
#                     if len(password) < 8:
#                         errors.append("Password has to be at least 8 characters!")
#                     for char in password:
#                         if char.upper():
#                             break
#                         errors.append("Password should contain at least 1 uppercase.")
#                 if errors:
#                     for e in errors:
#                         st.error(e)
#                 else:
#                     with st.spinner("Creating Account..."):
#                         time.sleep(1)
#                     result = manager.add_account_patient(username, password)

#                     if result:
#                         manager.save()
#                         st.session_state.username = username
#                         st.session_state.page = "patient"
#                         st.toast("Successfully registered")
#                         st.rerun()

# TODO: Reduce O(n) of password validation