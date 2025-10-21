import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# details manager functions
from helper_manager.profile_manager import (
    view_doctor_details,
    view_patient_details_by_doctor,
)

# Appointment manager
from helper_manager.appointment_manager import AppointmentManager

# Remark manager
from helper_manager.remark_manager import (
    view_patient_remarks,
    add_patient_remark,
    get_recent_patient_remarks,
    edit_patient_remark,
)

# ------------------------------------------------
# QUICK FIX: Safe update helper for doctor profile
# ------------------------------------------------
def update_doctor_details(manager, *, username,
                          new_password=None, new_name=None, new_gender=None,
                          new_address=None, new_email=None, new_contact_num=None,
                          new_department=None, new_speciality=None):
    """Update a doctor's fields by username and persist to JSON."""
    doc = next((d for d in manager.doctors if getattr(d, "username", None) == username), None)
    if not doc:
        return False
    if new_password:    doc.password = new_password
    if new_name:        doc.name = new_name
    if new_gender:      doc.gender = new_gender
    if new_address:     doc.address = new_address
    if new_email:       doc.email = new_email
    if new_contact_num: doc.contact_num = new_contact_num
    if new_department:  doc.department = new_department
    if new_speciality:  doc.speciality = new_speciality
    if hasattr(manager, "save"): manager.save()
    return True


# =========================
# DASHBOARD
# =========================
def dashboard(manager, username):
    """Main dashboard showing overview and quick stats"""
    st.divider()
    st.header("Dashboard Overview")

    # Doctor details
    success, message, profile = view_doctor_details(username)

    if profile:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Doctor ID", profile.get("staff_id", "N/A"))
        with col2:
            st.metric("Department", profile.get("department", "Not Set"))
        with col3:
            st.metric("Speciality", profile.get("speciality", "Not Set"))

        st.divider()

        st.header("Today's Appointments")
        appt_manager = AppointmentManager(manager)
        success, msg, appointments = appt_manager.view_upcoming_appointments(username)

        if success and appointments:
            today = datetime.now().strftime("%Y-%m-%d")  # ✅ fixed
            today_appts = [a for a in appointments if a.get("date") == today]
            if today_appts:
                for appt in today_appts[:3]:
                    st.info(
                        f"🕐 {appt.get('time','--:--')} - {appt.get('patient_name','Unknown')} ({appt.get('status','—')})"
                    )
            else:
                st.success("No appointments scheduled for today")
        else:
            st.info("No upcoming appointments")
    else:
        st.error(message)


# =========================
# PROFILE
# =========================
def profile_page(manager, username):
    """View and update doctor profile"""
    st.header("My Profile")

    success, message, profile = view_doctor_details(username)
    if not profile:
        st.error(message)
        return

    st.subheader("Current Profile Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=profile.get("name", ""), disabled=True)
        st.text_input("Email", value=profile.get("email", ""), disabled=True)
        st.text_input("Gender", value=profile.get("gender", ""), disabled=True)
        st.text_input("Date of Birth", value=profile.get("date_of_birth", ""), disabled=True)
    with col2:
        st.text_input("Contact Number", value=profile.get("contact_num", ""), disabled=True)
        st.text_area("Address", value=profile.get("address", ""), disabled=True)
        st.text_input("Department", value=profile.get("department", ""), disabled=True)
        st.text_input("Speciality", value=profile.get("speciality", ""), disabled=True)

    st.divider()
    st.subheader("Update Profile")

    with st.form("update_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("New Name (optional)")
            new_email = st.text_input("New Email (optional)")
            new_gender = st.selectbox("New Gender (optional)", ["", "Male", "Female", "Other"])
            new_password = st.text_input("New Password (optional)", type="password")
        with c2:
            new_contact = st.text_input("New Contact Number (optional)")
            new_address = st.text_area("New Address (optional)")
            new_department = st.text_input("New Department (optional)")
            new_speciality = st.text_input("New Speciality (optional)")

        submitted = st.form_submit_button("Update Profile")

        if submitted:
            ok = update_doctor_details(
                manager=manager,
                username=username,
                new_password=new_password or None,
                new_name=new_name or None,
                new_gender=new_gender or None,
                new_address=new_address or None,
                new_email=new_email or None,
                new_contact_num=new_contact or None,
                new_department=new_department or None,
                new_speciality=new_speciality or None,
            )
            if ok:
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update profile")


# =========================
# SEARCH UI
# =========================
def search_and_select_profile_ui(manager):
    role_map = {
        "patient": (manager.patients, "p_id"),
        "doctor": (manager.doctors, "d_id"),
        "nurse": (manager.nurses, "n_id"),
        "receptionist": (manager.receptionists, "r_id"),
    }

    st.subheader("Search Profiles")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        role = st.selectbox("Role", list(role_map.keys()))
    with col2:
        name_query = st.text_input("Name (partial ok)")
    with col3:
        trigger = st.button("Search", use_container_width=True)

    if not trigger:
        return False, None, None

    items, id_attr = role_map[role]
    nq = name_query.strip().lower()
    matches = [o for o in items if nq in getattr(o, "name", "").lower()]

    if not matches:
        st.warning(f"No {role} found matching '{name_query}'.")
        return False, None, None

    rows, idx = [], {}
    for o in matches:
        oid = getattr(o, id_attr)
        rows.append({
            "ID": oid,
            "Name": getattr(o, "name", ""),
            "Gender": getattr(o, "gender", ""),
            "Email": getattr(o, "email", ""),
            "Contact": getattr(o, "contact_num", ""),
            "Department": getattr(o, "department", ""),
            "Speciality": getattr(o, "speciality", ""),
            "Joined": getattr(o, "date_joined", ""),
        })
        idx[oid] = o

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    sel_id = st.selectbox(f"Select {role.capitalize()} ID", df["ID"].tolist())
    view = st.button("View profile", use_container_width=True)

    if view and sel_id:
        selected = idx.get(sel_id)
        if selected:
            st.subheader(f"{role.capitalize()} Profile: {sel_id}")
            for k, v in selected.__dict__.items():
                if k == "password":
                    continue
                st.write(f"**{k}**: {v}")
            return True, selected, role

    return False, None, None


# =========================
# PATIENT RECORDS (Remarks Only)
# =========================
def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    st.header("Patient Records & Remarks")

    tab1, tab2, tab3 = st.tabs(["View Patient Details", "Add Remark", "View Remarks"])

    # Tab 1: View Patient
    with tab1:
        st.markdown("#### Search by ID")
        patient_id = st.text_input("Enter Patient ID", key="patient_search_records")
        if st.button("Search Patient", key="search_btn"):
            success, message, info = view_patient_details_by_doctor(patient_id)
            if success and info:
                st.success(message)
                # Top-level metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Patient ID", info.get("patient_id", "N/A"))
                    st.metric("Name", info.get("name", "N/A"))
                    st.metric("Gender", info.get("gender", "N/A"))
                    st.metric("Date of Birth", info.get("date_of_birth", "N/A"))
                with col2:
                    # Normalize previous_conditions to a list of strings
                    raw_prev = info.get("previous_conditions", [])
                    prev_list = []
                    if isinstance(raw_prev, dict):
                        # dict of condition -> severity/notes
                        prev_list = [f"{k}: {v}" for k, v in raw_prev.items()]
                    elif isinstance(raw_prev, list):
                        prev_list = [str(x) for x in raw_prev]
                    elif isinstance(raw_prev, str):
                        prev_list = [raw_prev] if raw_prev.strip() else []

                    st.write("**Previous Conditions:**")
                    if prev_list:
                        for condition in prev_list:
                            st.write(f"• {condition}")
                    else:
                        st.info("No previous conditions recorded")

                    # Normalize medication_history to a list of strings
                    raw_med = info.get("medication_history", [])
                    med_list = []
                    if isinstance(raw_med, dict):
                        med_list = [f"{k}: {v}" for k, v in raw_med.items()]
                    elif isinstance(raw_med, list):
                        med_list = [str(x) for x in raw_med]
                    elif isinstance(raw_med, str):
                        med_list = [raw_med] if raw_med.strip() else []

                    st.write("**Medication History:**")
                    if med_list:
                        for med in med_list:
                            st.write(f"• {med}")
                    else:
                        st.info("No medication history recorded")
            else:
                st.error(message or "Patient not found.")

    # Tab 2: Add Remark
    with tab2:
        st.subheader("Add Patient Remark")
        with st.form("add_remark_form"):
            patient_id_remark = st.text_input("Enter Patient ID", key="patient_search_remark")
            remark_type = st.selectbox(
                "Remark Type", ["mood", "pain_level", "dietary", "general", "observation"]
            )
            remark_content = st.text_area("Remark Content", height=150)
            submitted = st.form_submit_button("Add Remark")

            if submitted:
                if not remark_content.strip():
                    st.error("Please enter remark content")
                else:
                    success, message, remark_id = add_patient_remark(
                        patient_id=patient_id_remark,
                        doctor_username=username,
                        remark_type=remark_type,
                        remark_content=remark_content,
                    )
                    if success:
                        st.success(f"✅ {message} (Remark ID: {remark_id})")
                    else:
                        st.error(message)

    # Tab 3: View/Edit Remarks
    with tab3:
        st.subheader("View Patient Remarks")
        view_patient_id = st.text_input("Enter Patient ID", key="patient_search_remark_view")
        filter_type = st.selectbox(
            "Filter by Type (optional)",
            ["All", "mood", "pain_level", "dietary", "general", "observation"],
        )
        days_filter = st.number_input("Recent Days", min_value=1, max_value=365, value=7)

        if st.button("View All Remarks"):
            remark_type_filter = None if filter_type == "All" else filter_type
            success, message, remarks = view_patient_remarks(
                patient_id=view_patient_id, remark_type=remark_type_filter
            )
            if success and remarks:
                for remark in remarks:
                    with st.expander(
                        f"{remark['remark_type'].upper()} - {remark['timestamp']} by {remark['doctor_name']}"
                    ):
                        st.write(remark["content"])
                        st.caption(f"Last Modified: {remark['last_modified']}")
                        if st.button(f"Edit {remark['remark_id']}"):
                            new_content = st.text_area("Edit Content", remark["content"])
                            if st.button("Save Edit"):
                                ok, msg = edit_patient_remark(
                                    remark_id=remark["remark_id"],
                                    doctor_username=username,
                                    new_content=new_content,
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
            else:
                st.info("No remarks found.")

        if st.button("View Recent Remarks"):
            success, message, remarks = get_recent_patient_remarks(
                patient_id=view_patient_id, days=days_filter
            )
            if success and remarks:
                for remark in remarks:
                    with st.expander(
                        f"{remark['remark_type'].upper()} - {remark['timestamp']}"
                    ):
                        st.write(f"**Doctor:** {remark['doctor_name']}")
                        st.write(remark["content"])
            else:
                st.info(f"No remarks found in the last {days_filter} days")


# =========================
# APPOINTMENTS
# =========================
def appointments_page(manager, username):
    """View and manage appointments"""
    st.header("Appointments")
    appt_manager = AppointmentManager(manager)
    success, message, appointments = appt_manager.view_upcoming_appointments(username)

    if not success:
        st.error(message)
        return

    if not appointments:
        st.info("No upcoming appointments scheduled")
        return

    st.success(message)
    c1, c2 = st.columns(2)
    with c1:
        enable_date_filter = st.checkbox("Filter by Date (optional)")
        filter_date = st.date_input("Pick a Date") if enable_date_filter else None
    with c2:
        filter_status = st.selectbox(
            "Filter by Status", ["All", "Pending", "Confirmed", "Completed", "Cancelled"]
        )

    filtered_appts = appointments
    if filter_date:
        target = filter_date.strftime("%Y-%m-%d")
        filtered_appts = [a for a in filtered_appts if a.get("date") == target]
    if filter_status != "All":
        filtered_appts = [a for a in filtered_appts if a.get("status") == filter_status]

    st.divider()
    if filtered_appts:
        for appt in filtered_appts:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**📅 {appt.get('date','—')}**")
                with col2:
                    st.write(f"**🕐 {appt.get('time','--:--')}**")
                with col3:
                    st.write(f"**👤 {appt.get('patient_name','Unknown')}** (ID: {appt.get('patient_id','—')})")
                with col4:
                    status_color = {
                        "Pending": "🟡", "Confirmed": "🟢", "Completed": "🔵", "Cancelled": "🔴",
                    }
                    st.write(f"{status_color.get(appt.get('status'), '⚪')} {appt.get('status','—')}")
                if appt.get("remark"):
                    st.caption(f"Note: {appt['remark']}")
                st.divider()
    else:
        st.info("No appointments match the selected filters")


# =========================
# SHIFT
# =========================
def shift_page(manager):
    manager = st.session_state.manager
    username = st.session_state.username
    doctor = next((d for d in manager.doctors if d.username == username), None)

    st.subheader("Shift Schedule")
    if not doctor:
        st.warning("No doctor found for this username.")
        return

    all_shifts = [s.__dict__ for s in manager.shifts if s.staff_id == doctor.d_id]
    if not all_shifts:
        st.info("No shifts assigned yet.")
        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = [f"{h:02d}:00" for h in range(8, 21)]
    schedule_df = pd.DataFrame(index=times, columns=days)
    schedule_df[:] = ""

    for shift in all_shifts:
        day = shift["day"]
        start = datetime.strptime(shift["start_time"], "%H:%M")
        end = datetime.strptime(shift["end_time"], "%H:%M")
        remark = shift["remark"]

        current = start
        while current < end:
            time_str = current.strftime("%H:00")
            if day in schedule_df.columns and time_str in schedule_df.index:
                schedule_df.loc[time_str, day] = remark
            current += timedelta(hours=1)

    st.dataframe(
        schedule_df.style.set_properties(
            subset=pd.IndexSlice[:, :],
            **{"text-align": "center", "white-space": "pre-wrap"}
        ),
        use_container_width=True,
        height=500
    )


# =========================
# ENTRYPOINT
# =========================
def doctor_page(_Manager):
    manager = st.session_state.manager
    username = st.session_state.username

    tabs = ["Dashboard", "Profile", "Patient Records", "Appointments", "Shift"]

    if st.session_state.get("logout_triggered"):
        st.session_state.logout_triggered = False
        st.rerun()

    st.title("🏥 CareLog")
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)

    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient Records":
        patient_records_page(manager, username)
    elif option == "Appointments":
        appointments_page(manager, username)
    elif option == "Shift":
        shift_page(manager)


def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True
    st.session_state.get_user_detail = ""
