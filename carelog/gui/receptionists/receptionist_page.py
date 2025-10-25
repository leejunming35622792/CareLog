import streamlit as st
import time
import datetime
from app.schedule import ScheduleManager
from app.receptionist import ReceptionistUser
from app.user import User
import app.utils as utils


def receptionist_page(receptionist: ReceptionistUser):
    # Variables
    manager = st.session_state.manager
    recep_uname = st.session_state.username
    current_receptionist = next((r for r in manager.receptionists if r.username == recep_uname), None)

    # Page design
    tabs = ["Dashboard", "Account", "Patient Search", "Appointments", "Profile"]

    # Sidebar
    username = st.session_state.username
    st.sidebar.title(f"CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Navigation", tabs)
    st.sidebar.button("Logout", on_click=logout)

    # ============================================================
    # DASHBOARD
    # ============================================================

    if option == "Dashboard":
        st.markdown("<h1 style='text-align: center;'>Welcome to CareLog!</h1>", unsafe_allow_html=True)
        st.balloons()
        st.image("img/dashboard.png")
        st.divider()

        st.header("Dashboard Overview 🎗️")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Receptionist ID", current_receptionist.r_id)
        with col2:
            if current_receptionist.name:
                disp = current_receptionist.name
            else:
                disp = ""
            st.metric("Name", disp)
        with col3:
            if current_receptionist.email:
                disp = current_receptionist.email
            else:
                disp = ""
            st.metric("Name", disp)
        st.divider()

        st.header("System Overview 🧰")
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Total Patients", len(manager.patients))
        with col5:
            st.metric("Total Doctors", len(manager.doctors))
        with col6:
            st.metric("Total Appointments", len(manager.appointments))

    # ============================================================
    # CREATE PATIENT ACCOUNT
    # ============================================================
    elif option == "Account":
        from app.admin import AdminUser
        st.header("Register New Patient 👤")
        role = "patient"
        user_id = User.get_next_id(manager, role)
        success, message = "", ""
        # Why receptionist.get_next_id here but not user?
        # ReceptionistUser is a subclass of user, so it will 

        with st.form("register_form"):
            st.subheader("Account Information")
            col1, col2 = st.columns(2)
            with col1:
                patient_role = st.text_input("Select Role", value=role.title(), disabled=True)
            with col2:
                patient_id = st.text_input("Assigned ID", user_id, disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                input_username = st.text_input("Username: ", value=username)
            with col2:
                input_password = st.text_input("Password", type="password")

            st.divider()
            st.subheader("Personal Information")
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
                contact_num = st.text_input("Enter Contact Number: ", placeholder="+6012-3456789")

            col7, col8 = st.columns(2)
            with col7:
                birthday = st.date_input("Enter Birthday: ", min_value="1920-01-01", max_value="today")
            with col8:
                current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                date_joined = st.text_input("Date Joined:", value=current_datetime, disabled=True)

            submitted = st.form_submit_button("Create Account")

            if submitted:
                with st.spinner("Processing..."):
                    time.sleep(1.5)
                success, message, user_obj = User.create_user(manager, role, user_id, input_username, input_password, name, birthday, gender, address, email, contact_num, date_joined, None, None, None)
                if success:
                    st.session_state.success_msg = message
                    utils.log_event(f"Receptionist {current_receptionist.username} created new patient {username}", "INFO")
                    st.rerun()
                else:
                    for error in message:
                        st.error(error)
                    utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")

    # ============================================================
    # PATIENT SEARCH
    # ============================================================
    elif option == "Patient Search":
        st.header("🔍 Search Patients")

        # Search bar
        query = st.text_input("Enter name, patient ID, email or contact: ")
        if query:
            results = receptionist.search_patients(query)
            if results:
                st.success(f"Found {len(results)} patients.")
                for p in results:
                    with st.expander(f"{p.name} ({p.p_id})"):
                        st.write(f"**Gender:** {p.gender}")
                        st.write(f"**Email:** {p.email}")
                        st.write(f"**Contact:** {p.contact_num}")
                        st.write(f"**Address:** {p.address}")
                        st.write(f"**DOB:** {p.dob}")
                        st.write(f"**Remarks:** {p.remarks}")
                        st.write(f"**Date Joined:** {p.date_joined}")
                        st.divider()
            else:
                st.warning("No patients found.")
        else:
            st.info("Type something to search.")
    
    # ============================================================
    # APPOINTMENTS
    # ============================================================
    elif option == "Appointments":
        st.header("📅 Appointment Management")
        tab1, tab2, tab3 = st.tabs(["Create Appointment", "View Appointments", "Update Status"])

        # Create Appointment
        with tab1:
            st.subheader("➕ Create New Appointment")
            patient_id = st.selectbox("Select Patient", [p.p_id for p in manager.patients])
            doctor_id = st.selectbox("Select Doctor", [d.d_id for d in manager.doctors])
            date = st.date_input("Appointment Date")
            time_ = st.time_input("Appointment Time")

            if st.button("Create Appointment"):
                success, message, _ = receptionist.create_appointment(patient_id, doctor_id, date.isoformat(), str(time_))
                if success:
                    st.success(message)
                else:
                    st.error(message)

        # View Appointment
        with tab2:
            st.subheader("📋 All Appointments")
            if manager.appointments:
                for a in manager.appointments:
                    st.write(f"**{a['appt_id']}** - {a['patient_id']} with {a['doctor_id']} on {a['date']} at {a['time']} ({a['status']})")
            else:
                st.info("No appointments found.")

        # Update Status
        with tab3:
            st.subheader("✏️ Update Appointment Status")
            appt_id = st.text_input("Enter Appointment ID")
            new_status = st.selectbox("New Status", ["Scheduled", "Completed", "Cancelled"])
            if st.button("Update Status"):
                success, message = receptionist.update_appointment_status(appt_id, new_status)
                if success:
                    st.success(message)
                else:
                    st.error(message)
                    
    # ============================================================
    # PROFILE TAB
    # ============================================================
    elif option == "Profile":
        st.header("🧍 My Profile")
        st.write(f"**Username:** {receptionist.username}")
        st.write(f"**Name:** {receptionist.name}")
        st.write(f"**Email:** {receptionist.email}")
        st.write(f"**Contact:** {receptionist.contact_num}")
        st.write(f"**Date Joined:** {receptionist.date_joined}")

    if "success_msg" in st.session_state and st.session_state.success_msg != "":
        st.success(st.session_state.success_msg)
        st.balloons()
        del st.session_state.success_msg

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True