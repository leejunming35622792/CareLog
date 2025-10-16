import streamlit as st
import time
from app.schedule import ScheduleManager
from app.receptionist import ReceptionistUser
from app.user import User as user
import app.utils as utils

def receptionist_page(receptionist: ReceptionistUser):
    sc = ScheduleManager()
    st.title("🏥 Receptionist Dashboard")
    tabs = ["Dashboard", "Account", "Patient Search", "Appointments", "Profile"]

    # Sidebar
    username = st.session_state.get("username", receptionist.username)
    st.sidebar.title(f"Welcome, {username}")
    option = st.sidebar.radio("Navigation", tabs)
    st.sidebar.button("Logout", on_click=logout)

    # ============================================================
    # DASHBOARD
    # ============================================================
    if option == "Dashboard":
        st.header("📊 Overview")
        st.write(f"Logged in as: **{username}**")
        st.metric("Total Patients", len(sc.patients))
        st.metric("Total Doctors", len(sc.doctors))
        st.metric("Total Appointments", len(sc.appointments))

    # ============================================================
    # CREATE PATIENT ACCOUNT
    # ============================================================
    elif option == "Account":
        from app.admin import AdminUser
        st.header("👤 Register New Patient")
        role = "Patient"
        user_id = receptionist.get_next_id(role)
        # Why receptionist.get_next_id here but not user?
        # ReceptionistUser is a subclass of user, so it will 

        with st.form("register_form"):
            st.text_input("Role", role, disabled=True)
            st.text_input("Assigned ID", user_id, disabled=True)

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Create Account")
            if submitted:
                with st.spinner("Registering..."):
                    time.sleep(1)
                success, message, _ = receptionist.register_user(role, username, password)

            if success:
                sc.save()
                st.success(message)
                st.toast(f"{role} account successfully created!")
                utils.log_event(f"Receptionist {receptionist.username} created new patient {username}", "INFO")
                st.rerun()
            else:
                utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")
                st.error(message)

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
            patient_id = st.selectbox("Select Patient", [p.p_id for p in sc.patients])
            doctor_id = st.selectbox("Select Doctor", [d.d_id for d in sc.doctors])
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
            if sc.appointments:
                for a in sc.appointments:
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

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True