import streamlit as st
import time

def create_account(manager):
    # Variables
    all_username = [p.username for p in manager.patients] + [d.username for d in manager.doctors] + [n.username for n in manager.nurses] + [r.username for r in manager.receptionists] + [a.username for a in manager.admins]

    col1, col2 = st.columns(2)

    with col1:
        st.image("C:\\Users\\Owner\\FIT1056-Sem2-2025\\carelog\\img\\wallpaper.jpg")

    with col2:
        with st.form("register-form"):
            st.subheader("Create Account")
            username = st.text_input("Username: ")
            password = st.text_input("Password: ")
            name = None
            button = st.form_submit_button("Create Account")

            if button:
                # Variables
                errors = []

                if not username:
                    errors.append("Username cannot be empty!")
                else:
                    if username in all_username:
                        errors.append("Username has been taken!")
                if not password:
                    errors.append("Password cannot be empty!")
                else:
                    if len(password) < 8:
                        errors.append("Password has to be at least 8 characters!")
                    for char in password:
                        if char.upper():
                            break
                        errors.append("Password should contain at least 1 uppercase.")
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    with st.spinner("Creating Account..."):
                        time.sleep(1)
                    result = manager.add_account_patient(username, password)

                    if result:
                        manager.save()
                        st.session_state.username = username
                        st.session_state.page = "patient"
                        st.toast("Successfully registered")
                        st.rerun()

# TODO: Reduce O(n) of password validation