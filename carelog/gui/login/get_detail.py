import streamlit as st
import time, datetime
import app.utils as utils

def get_detail(role, username, password, user_id):
    from app.user import User
    user = User("","","","","","","","", "")
    
    # Variable
    manager = st.session_state.manager
    success, message = "", ""

    st.title("CareLog Sign Up")

    with st.form("get-detail-form"):
        st.subheader("Personal Details")
        st.info("You are almost there! 😉")

        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username: ", value=f"@{username}", disabled=True)
        with col2:
            password = st.text_input("Password", value=password, disabled=True)

        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            name = st.text_input("Enter Name: ")
        with col4:
            gender = st.selectbox("Select Gender: ", ["Male", "Female", "Prefer Not to Say"])

        col5, col6 = st.columns(2)
        with col5:
            address = st.text_area("Enter Home Address: ")
        with col6:
            email = st.text_input("Enter Email Address:")
            contact_num = st.text_input("Enter Contact Number: ", placeholder="+601X-XXXXXXX")

        col7, col8 = st.columns(2)
        with col7:
            birthday = st.date_input("Enter Birthday: ")
        with col8:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_joined = st.text_input("Date Joined:", value=current_datetime, disabled=True)

        if role in ["Doctor", "Nurse"]:
            speciality = st.text_input("Enter Speciality: ")
            department = st.text_input("Enter Department: ")
            if role == "Nurse":
                doctor_disp = {f"{d.d_id} - {d.name}": d.id for d in manager.doctors}
                with_doctor_input = st.selectbox("With Doctor: ", doctor_disp.keys())
                with_doctor = doctor_disp[with_doctor_input]

        continue_button = st.form_submit_button("Continue")

        if continue_button:
            with st.spinner("Processing..."):
                time.sleep(1.5)
                role = role.lower()     
                birthday = str(birthday)           
                if role == "patient": 
                    success, message, user_obj = user.create_user(manager, role, user_id, username, password, name, birthday, gender, address, email, contact_num, date_joined, None, None, None)
                elif role == "doctor":
                    success, message, user_obj = user.create_user(manager, role, user_id, username, password, name, birthday, gender, address, email, contact_num, date_joined, speciality, department, None)
                elif role == "nurse":
                    success, message, user_obj = user.create_user(manager, role, user_id, username, password, name, birthday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor)
                elif role == "receptionist":
                    success, message, user_obj = user.create_user(manager, role, user_id, username, password, name, birthday, gender, address, email, contact_num, date_joined, None, None, None)
                
                st.session_state.get_user_detail = ""

                if success:
                    manager.save()
                    utils.log_event(f"{role} {username} registered successfully.", "INFO")
                    st.success(message)
                    st.toast(f"Welcome, {username}!")
                    st.session_state.username = username
                    st.session_state.page = role.lower()
                    st.rerun()
                else:
                    print(message)
                    utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")
                    st.error(message)