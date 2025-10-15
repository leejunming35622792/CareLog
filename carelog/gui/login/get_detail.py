import streamlit as st
import time, datetime
import app.utils as utils

def get_detail(role, username, password, user_id):
    from app.user import User
    manager = st.session_state.manager
    st.title("CareLog Sign Up")
    with st.form("get-detail-form"):
        st.subheader("Personal Details")
        st.info("You are almost there! 😉")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Enter Name: ")
        with col2:
            gender = st.selectbox("Select Gender: ", ["Male", "Female", "Prefer Not to Say"])

        col3, col4 = st.columns(2)
        with col3:
            address = st.text_area("Enter Home Address: ")
        with col4:
            email = st.text_input("Enter Email Address:")
            contact_num = st.text_input("Enter Contact Number: ", placeholder="+601X-XXXXXXX")

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_joined = st.text_input("Date Joined:", value=current_datetime, disabled=True)

        if role in ["Doctor", "Nurse"]:
            speciality = st.text_input("Enter Speciality: ")
            department = st.text_input("Enter Department: ")
            if role == "Nurse":
                doctor_disp = {f"{d.d_id} - {d.name}": d.id for d in manager.doctors}
                with_doctor_input = st.select_box("With Doctor: ", doctor_disp.keys())
                with_doctor = doctor_disp[with_doctor_input]

        continue_button = st.form_submit_button("Continue")

        if continue_button:
            with st.spinner("Processing..."):
                time.sleep(1.5)
                
                if role == "patient":
                    success, message, user_obj = User.create_user(manager, role, user_id, username, password, name, gender, address, email, contact_num, date_joined, None, None, None)
                elif role == "doctor":
                    success, message, user_obj = User.create_user(manager, role, user_id, username, password, name, gender, address, email, contact_num, date_joined, speciality, department, None)
                elif role == "nurse":
                    success, message, user_obj = User.create_user(manager, role, user_id, username, password, name, gender, address, email, contact_num, date_joined, speciality, department, with_doctor)
                elif role == "receptionist":
                    success, message, user_obj = User.create_user(manager, role, user_id, username, password, name, gender, address, email, contact_num, date_joined, None, None, None)
                
                st.session_state.get_user_detail = ""
                success, message, user_obj = User.create_user(manager, role, username, password, user_id)

                if success:
                    manager.save()
                    utils.log_event(f"{role} {username} registered successfully.", "INFO")
                    st.success(message)
                    st.toast(f"Welcome, {username}!")
                    st.session_state.username = username
                    st.session_state.page = role.lower()
                    st.rerun()
                else:
                    utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")
                    st.error(message)
        