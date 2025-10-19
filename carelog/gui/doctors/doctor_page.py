import streamlit as st
import datetime
import pandas as pd
from helper_manager.profile_manager import view_doctor_details 
from helper_manager.appointment_manager import AppointmentManager

manager = st.session_state.manager
appt_manager = AppointmentManager(manager)

def dashboard(username):
    """Main dashboard showing overview and quick stats"""
    
    # Page design
    st.divider()
    st.header("Dashboard Overview")
    
    # Get doctor details
    password = st.session_state.get('password', '')
    success, message, profile = view_doctor_details(username)
    
    if profile:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Doctor ID", profile.get('staff_id', 'N/A'))
        with col2:
            st.metric("Department", profile.get('department', 'Not Set'))
        with col3:
            st.metric("Speciality", profile.get('speciality', 'Not Set'))
        
        st.divider()

        # Upcoming appointments preview
        st.header("Today's Appointments")
        success, msg, appointments = appt_manager.view_upcoming_appointments(username)
        if success and appointments:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            today_appts = [a for a in appointments if a['date'] == today]
            if today_appts:
                for appt in today_appts[:3]:  # Show first 3
                    st.info(f"🕐 {appt['time']} - {appt['patient_name']} ({appt['status']})")
            else:
                st.success("No appointments scheduled for today")
        else:
            st.info("No upcoming appointments")
    else:
        st.error(message)


def profile_page(manager, username):
    """View and update doctor profile"""
    st.header("My Profile")
    
    password = st.session_state.get('password', '')
    success, message, profile = view_doctor_details(username)
    
    if profile:
        # Display current profile
        st.subheader("Current Profile Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Name", value=profile.get('name',''), disabled=True)
            st.text_input("Email", value=profile.get('email', ''), disabled=True)
            st.text_input("Gender", value=profile.get('gender', ''), disabled=True)
            st.text_input("Date of Birth", value=profile.get('date_of_birth', ''), disabled=True)
        
        with col2:
            st.text_input("Contact Number", value=profile.get('contact_num', ''), disabled=True)
            st.text_area("Address", value=profile.get('address', ''), disabled=True)
            st.text_input("Department", value=profile.get('department', ''), disabled=True)
            st.text_input("Speciality", value=profile.get('speciality', ''), disabled=True)
        
        st.divider()
        
        # Update profile section
        st.subheader("Update Profile")
        
        with st.form("update_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("New Name (optional)")
                new_email = st.text_input("New Email (optional)")
                new_gender = st.selectbox("New Gender (optional)", ["", "Male", "Female", "Other"])
                new_password = st.text_input("New Password (optional)", type="password")
            
            with col2:
                new_contact = st.text_input("New Contact Number (optional)")
                new_address = st.text_area("New Address (optional)")
                new_department = st.text_input("New Department (optional)")
                new_speciality = st.text_input("New Speciality (optional)")
            
            submitted = st.form_submit_button("Update Profile")
            
            if submitted:
                success = manager.update_doctor_details(
                    username=username,
                    new_password=new_password if new_password else None,
                    new_name=new_name if new_name else None,
                    new_gender=new_gender if new_gender else None,
                    new_address=new_address if new_address else None,
                    new_email=new_email if new_email else None,
                    new_contact_num=new_contact if new_contact else None,
                    new_department=new_department if new_department else None,
                    new_speciality=new_speciality if new_speciality else None
                )
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile")
    else:
        st.error(message)

def search_and_select_profile_ui(manager):
    role_map = {
        "patient":      (manager.patients,      "p_id"),
        "doctor":       (manager.doctors,       "d_id"),
        "nurse":        (manager.nurses,        "n_id"),
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
        return False, None, None  # (found, selected_obj, selected_role)

    items, id_attr = role_map[role]
    matches = [o for o in items if name_query.strip().lower() in getattr(o, "name", "").lower()]

    if not matches:
        st.warning(f"No {role} found matching '{name_query}'.")
        return False, None, None

    # Build table
    rows = []
    idx = {}
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

def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    st.header("Patient Records & Remarks")
    
    tab1, tab2, tab3 = st.tabs(["View Patient Details", "Add Remark", "View Remarks"])
    
    with tab1:
        st.markdown("#### Search by Name")
        found, selected, role = search_and_select_profile_ui(manager)
        if found and selected and role == "patient":
            st.success("Patient selected from search.")
            info_ok, info_msg, info = manager.view_patient_details_by_doctor(selected.p_id)
            if info_ok:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Patient ID", info['patient_id'])
                    st.metric("Name", info['name'])
                    st.metric("Gender", info['gender'])
                    st.metric("Date of Birth", info.get('date_of_birth', 'N/A'))
                with col2:
                    st.write("**Previous Conditions:**")
                    if info['previous_conditions']:
                        for c in info['previous_conditions']:
                            st.write(f"• {c}")
                    else:
                        st.info("No previous conditions recorded")

                    st.write("**Medication History:**")
                    if info['medication_history']:
                        for m in info['medication_history']:
                            st.write(f"• {m}")
                    else:
                        st.info("No medication history recorded")
            else:
                st.error(info_msg)

        st.divider()
        st.markdown("#### Search by ID")
        patient_id = st.number_input("Enter Patient ID", min_value=1, step=1, key="patient_search")
        if st.button("Search Patient", key="search_btn"):
            success, message, info = manager.view_patient_details_by_doctor(patient_id)
            if success:
                st.success(message)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Patient ID", info['patient_id'])
                    st.metric("Name", info['name'])
                    st.metric("Gender", info['gender'])
                    st.metric("Date of Birth", info.get('date_of_birth', 'N/A'))
                with col2:
                    st.write("**Previous Conditions:**")
                    if info['previous_conditions']:
                        for condition in info['previous_conditions']:
                            st.write(f"• {condition}")
                    else:
                        st.info("No previous conditions recorded")
                    st.write("**Medication History:**")
                    if info['medication_history']:
                        for med in info['medication_history']:
                            st.write(f"• {med}")
                    else:
                        st.info("No medication history recorded")
            else:
                st.error(message)
    
    with tab2:
        st.subheader("Add Patient Remark")
        
        with st.form("add_remark_form"):
            patient_id_remark = st.number_input("Patient ID", min_value=1, step=1, key="remark_patient_id")
            remark_type = st.selectbox(
                "Remark Type",
                ["mood", "pain_level", "dietary", "general", "observation"]
            )
            remark_content = st.text_area("Remark Content", height=150)
            
            submitted = st.form_submit_button("Add Remark")
            
            if submitted:
                if not remark_content.strip():
                    st.error("Please enter remark content")
                else:
                    success, message, remark_id = manager.add_patient_remark(
                        patient_id=patient_id_remark,
                        doctor_username=username,
                        remark_type=remark_type,
                        remark_content=remark_content
                    )
                    
                    if success:
                        st.success(f"✅ {message} (Remark ID: {remark_id})")
                    else:
                        st.error(message)
    
    with tab3:
        st.subheader("View Patient Remarks")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            view_patient_id = st.number_input("Patient ID", min_value=1, step=1, key="view_remarks_patient_id")
        with col2:
            filter_type = st.selectbox("Filter by Type (optional)", 
                                      ["All", "mood", "pain_level", "dietary", "general", "observation"])
        with col3:
            days_filter = st.number_input("Recent Days", min_value=1, max_value=365, value=7)
        
        col_a, col_b = st.columns(2)
        with col_a:
            view_all = st.button("View All Remarks", key="view_all_remarks")
        with col_b:
            view_recent = st.button("View Recent Remarks", key="view_recent_remarks")
        
        if view_all:
            remark_type_filter = None if filter_type == "All" else filter_type
            success, message, remarks = manager.view_patient_remarks(
                patient_id=view_patient_id,
                remark_type=remark_type_filter
            )
            
            if success:
                st.info(message)
                if remarks:
                    for remark in remarks:
                        with st.expander(f"{remark['remark_type'].upper()} - {remark['timestamp']} by {remark['doctor_name']}"):
                            st.write(remark['content'])
                            st.caption(f"Last Modified: {remark['last_modified']}")
                            
                            # Edit remark option
                            if st.button(f"Edit", key=f"edit_{remark['remark_id']}"):
                                st.session_state[f"editing_{remark['remark_id']}"] = True
                            
                            if st.session_state.get(f"editing_{remark['remark_id']}", False):
                                new_content = st.text_area(
                                    "New Content",
                                    value=remark['content'],
                                    key=f"new_content_{remark['remark_id']}"
                                )
                                col_x, col_y = st.columns(2)
                                with col_x:
                                    if st.button("Save", key=f"save_{remark['remark_id']}"):
                                        edit_success, edit_msg = manager.edit_patient_remark(
                                            remark_id=remark['remark_id'],
                                            doctor_username=username,
                                            new_content=new_content
                                        )
                                        if edit_success:
                                            st.success(edit_msg)
                                            st.session_state[f"editing_{remark['remark_id']}"] = False
                                            st.rerun()
                                        else:
                                            st.error(edit_msg)
                                with col_y:
                                    if st.button("Cancel", key=f"cancel_{remark['remark_id']}"):
                                        st.session_state[f"editing_{remark['remark_id']}"] = False
                                        st.rerun()
                else:
                    st.info("No remarks found")
            else:
                st.error(message)
        
        if view_recent:
            success, message, remarks = manager.get_recent_patient_remarks(
                patient_id=view_patient_id,
                days=days_filter
            )
            
            if success:
                st.info(message)
                if remarks:
                    for remark in remarks:
                        with st.expander(f"{remark['remark_type'].upper()} - {remark['timestamp']}"):
                            st.write(f"**Doctor:** {remark['doctor_name']}")
                            st.write(remark['content'])
                else:
                    st.info(f"No remarks found in the last {days_filter} days")
            else:
                st.error(message)


def appointments_page(manager, username):
    pass
    # """View and manage appointments"""
    # st.header("Appointments")
    
    # success, message, appointments = appt_manager.view_upcoming_appointments(username)
    
    # if success:
    #     st.success(message)
        
    #     if appointments:
    #         # Filter options
    #         col1, col2 = st.columns(2)
    #         with col1:
    #             enable_date_filter = st.checkbox("Filter by Date (optional)")
    #             filter_date = st.date_input("Pick a Date") if enable_date_filter else None
    #         with col2:
    #             filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Confirmed", "Completed", "Cancelled"])
            
    #         # Apply filters
    #         filtered_appts = appointments
    #         if filter_date:
    #             filtered_appts = [a for a in filtered_appts if a['date'] == filter_date.strftime("%Y-%m-%d")]
    #         if filter_status != "All":
    #             filtered_appts = [a for a in filtered_appts if a['status'] == filter_status]
            
    #         st.divider()
            
    #         if filtered_appts:
    #             for appt in filtered_appts:
    #                 with st.container():
    #                     col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
    #                     with col1:
    #                         st.write(f"**📅 {appt['date']}**")
    #                     with col2:
    #                         st.write(f"**🕐 {appt['time']}**")
    #                     with col3:
    #                         st.write(f"**👤 {appt['patient_name']}** (ID: {appt['patient_id']})")
    #                     with col4:
    #                         status_color = {
    #                             "Pending": "🟡",
    #                             "Confirmed": "🟢",
    #                             "Completed": "🔵",
    #                             "Cancelled": "🔴"
    #                         }
    #                         st.write(f"{status_color.get(appt['status'], '⚪')} {appt['status']}")
                        
    #                     if appt['remark']:
    #                         st.caption(f"Note: {appt['remark']}")
                        
    #                     st.divider()
    #         else:
    #             st.info("No appointments match the selected filters")
    #     else:
    #         st.info("No upcoming appointments scheduled")
    # else:
    #     st.error(message)


def doctor_page(Manager):
    """Main doctor page with navigation"""
    manager = st.session_state.manager
    username = st.session_state.username
    
    # Store password in session state if not already there
    #if 'password' not in st.session_state:
       # st.session_state.password = ''
    
    tabs = ["Dashboard", "Profile", "Patient Records", "Appointments"]

    # Session state for logout
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.title(f"🏥 CareLog Dashboard")
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)

    # Route to appropriate page
    if option == "Dashboard":
        dashboard(username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient Records":
        patient_records_page(manager, username)
    elif option == "Appointments":
        appointments_page(manager, username)


def logout():
    """Handle logout"""
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True
    st.session_state.username = ""
    st.session_state.get_user_detail = ""