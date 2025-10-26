import streamlit as st
import datetime
import time
import pandas as pd
import app.utils as utils
from app.schedule import ScheduleManager
from app.receptionist import ReceptionistUser
from app.user import User
from helper_manager.record_manager import (update_record_receptionist)
from helper_manager.shift_manager import (create_shift, get_all_shift, shift_convert_df)

def receptionist_page(manager: ScheduleManager):
    # Variables
    recep_uname = st.session_state.username
    current_receptionist = next((r for r in manager.receptionists if r.username == recep_uname), None)

    # Page design
    tabs = ["Dashboard", "Register", "Patient", "Appointments", "Shift", "Profile"]

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
            st.metric("Email", disp)
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
    elif option == "Register":
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
                birthday = st.date_input("Enter Birthday: ", min_value=datetime.date(1920, 1, 1), max_value=datetime.date.today())
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
                    utils.log_event(f"Receptionist {current_receptionist.username} created new patient {input_username}", "INFO")
                    st.rerun()
                else:
                    for error in message:
                        st.error(error)
                    utils.log_event(f"Failed registration for {role} ({input_username}): {message}", "ERROR")

    # ============================================================
    # PATIENT SEARCH
    # ============================================================
    elif option == "Patient":
        tab1, tab2 = st.tabs(["Search Patient", "Edit Records"])

        with tab1:
            st.header("🔍 Search Patients")

            # Search bar
            query = st.text_input("Enter name, patient ID, email or contact: ")
            if query:
                results = current_receptionist.search_patients(query, manager)
                if results:
                    st.success(f"Found {len(results)} patients.")
                    for p in results:
                        with st.expander(f"{p.name} ({p.p_id})"):
                            st.write(f"**Gender:** {p.gender}")
                            st.write(f"**Email:** {p.email}")
                            st.write(f"**Contact:** {p.contact_num}")
                            st.write(f"**Address:** {p.address}")
                            st.write(f"**DOB:** {p.bday}")
                            st.write(f"**Remarks:** {p.remark}")
                            st.write(f"**Date Joined:** {p.date_joined}")
                            st.divider()
                else:
                    st.warning("No patients found.")
            else:
                st.info("Type something to search.")
        with tab2:
            patient_disp = {f"{p.p_id} : {p.name}": p.p_id for p in manager.patients}
            if not patient_disp:
                st.warning("No patients found")
                st.stop()
            
            select_patient = st.selectbox("Select Patient", patient_disp.keys())
            patient_id = patient_disp[select_patient]

            record_disp = {f"{r.pr_record_id} - {datetime.datetime.fromisoformat(r.pr_timestamp).strftime("%d/%m/%Y")}":r.pr_record_id for r in manager.records if r.p_id == patient_id}

            if not record_disp:
                st.warning(f"No records found for patient '{patient_id}'")
                st.stop()

            select_record = st.selectbox("Select Record", record_disp.keys())
            record = record_disp[select_record]

            with st.form("update_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pr_record_id = st.text_input("📋 Record ID", record["pr_record_id"], disabled=True)
                    p_id = st.text_input("🧾 Patient ID", record["p_id"], disabled=True)
                    pr_timestamp = st.text_input("⏰ Timestamp", record["pr_timestamp"], disabled=True)
                    pr_billings = st.number_input("💵 Billing Amount (RM)", value=record["pr_billings"], step=1.0)

                with col2:
                    pr_conditions = st.text_area("💉 Condition / Diagnosis", record["pr_conditions"], disabled=True)
                    pr_medications = st.text_input("💊 Medications", record["pr_medications"], disabled=True)
                    pr_remark = st.text_area("🩹 Doctor’s Remark", record["pr_remark"], height=100, disabled=True)

                submitted = st.form_submit_button("Save Changes 💾")

                if submitted and pr_billings:
                    result = update_record_receptionist(manager, pr_record_id, pr_billings)
                    if result:
                        st.session_state.success_msg = result
                        manager.save()
                    else:
                        st.warning("Unexpected error")
                else:
                    st.warning("⚠️ Please save with a billing amount")
    
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
                success, message, _ = current_receptionist.create_appointment(manager, patient_id, doctor_id, date.isoformat(), str(time_))
                if success:
                    st.success(message)
                else:
                    st.error(message)

        # View Appointment
        with tab2:
            st.subheader("📋 All Appointments")
            if manager.appointments:
                for a in manager.appointments:
                    st.write(f"**{a.appt_id}** – {a.p_id} with {a.d_id} on {a.date} at {a.time} ({a.status})")
            else:
                st.info("No appointments found.")

        # Update Status
        with tab3:
            st.subheader("✏️ Update Appointment Status")
            appt_id = st.text_input("Enter Appointment ID")
            new_status = st.selectbox("New Status", ["Scheduled", "Completed", "Cancelled"])
            if st.button("Update Status"):
                success, message = current_receptionist.update_appointment_status(manager, current_receptionist.username, appt_id, new_status)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    # ============================================================
    # SHIFT
    # ============================================================  
    elif option == "Shift":
        tab1, tab2 = st.tabs(["Create Shift", "View Shift"])
        with tab1:
            st.markdown(
            "<h2 style='text-align: center; color: #2c3e50;'>🕒 Create New Shift</h2>",
            unsafe_allow_html=True
            )

            # Get next Shift ID
            shift_id = manager.next_shift_id

            # Combine all doctors and nurses
            all_staff = []
            for doc in getattr(manager, "doctors", []):
                all_staff.append(f"{doc.d_id} - {doc.name}")
            for nurse in getattr(manager, "nurses", []):
                all_staff.append(f"{nurse.n_id} - {nurse.name}")

            # Input boxes
            with st.form("create_shift_form"):
                st.text_input("🆔 Shift ID", shift_id, disabled=True)

                staff_choice = st.selectbox("Select Staff Member 👩‍⚕️", all_staff)

                # Extract ID
                selected_id = staff_choice.split(" - ")[0]

                # Shift scheduling info
                col1, col2 = st.columns(2)
                with col1:
                    day = st.selectbox(
                        "Day 📅",
                        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    )
                with col2:
                    remark = st.text_input("Remark (optional) 📝")

                col3, col4 = st.columns(2)
                with col3:
                    start_time = st.time_input("Start Time 🕓", value=datetime.time(9, 0))
                with col4: 
                    end_time = st.time_input("End Time 🕔", value=datetime.time(17, 0))

                submitted = st.form_submit_button("💾 Create Shift")

                if submitted:
                    success, msg = create_shift(manager, shift_id, staff_choice, day, start_time, end_time, remark)
                    with st.spinner("Processing"):
                        time.sleep(1.5)
                    if success:
                        st.session_state.success_msg = success
                        manager.save()
                        st.rerun()
                    else:
                        st.warning(msg)

        with tab2:
            all_shifts = get_all_shift(manager, "receptionist")
            records = shift_convert_df(all_shifts)

            if records.empty():
                st.warning("No shifts found")
                st.stop()

            st.title("Shift Schedule 📅")

            with st.expander("Filter Options 🔍", expanded=True):
                col1, col2, col3 = st.columns(3)

                # Filter by staff name/id
                staff_options = sorted(records["Staff"].unique())
                staff_filter = col1.multiselect("Filter by Staff", staff_options, default=staff_options)

                # Filter by day
                day_options = sorted(records["Day"].unique())
                day_filter = col2.multiselect("Filter by Day", day_options, default=day_options)

                # Filter by time range
                start_time_filter, end_time_filter = col3.slider(
                    "Filter by Start Time Range (hour)", 0, 24, (0, 24)
                )

            # Filters 
            filtered_records = records[
                records["Staff"].isin(staff_filter)
                & records["Day"].isin(day_filter)
            ]

            # If times are strings
            def time_to_hour(t):
                try:
                    return int(str(t).split(":")[0])
                except:
                    return 0
            filtered_records = filtered_records[
                filtered_records["Start Time"].apply(time_to_hour).between(start_time_filter, end_time_filter)
            ]

            # Display table 
            st.dataframe(filtered_records, use_container_width=True)

            st.caption(f"Showing {len(filtered_records)} shifts.")

    # ============================================================
    # PROFILE TAB
    # ============================================================
    elif option == "Profile":
        st.header("🧍 My Profile")
        st.write(f"**Username:** {current_receptionist.username}")
        st.write(f"**Name:** {current_receptionist.name}")
        st.write(f"**Email:** {current_receptionist.email}")
        st.write(f"**Contact:** {current_receptionist.contact_num}")
        st.write(f"**Date Joined:** {current_receptionist.date_joined}")

    if "success_msg" in st.session_state and st.session_state.success_msg != "":
        st.success(st.session_state.success_msg)
        st.balloons()
        del st.session_state.success_msg

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True