import streamlit as st
import datetime
from app.nurse import NurseUser
from gui.nurses.nurse_dashboard import dashboard
from gui.nurses.nurse_profile import profile_page


def appointments_page(manager, username):
    """Appointments Management Page"""
    st.header("📅 Appointments Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "View Appointments",
        "Create Appointment", 
        "Update Appointment",
        "Cancel Appointment"
    ])
    
    #View Appointments
    with tab1:
        st.subheader("🔍 View Appointments")
        view_option = st.radio("View by:", ["All Appointments", "By Appointment ID", "By Patient ID", "By Date"], horizontal=True)
        
        if view_option == "All Appointments":
            if st.button("Show All Appointments"):
                success, msg, appts = manager.view_appointment_nurse()
                if success:
                    st.success(msg)
                    for appt in appts:
                        with st.expander(f"Appointment {appt['appt_id']} - {appt['date']} {appt['time']}"):
                            st.write(f"**Patient:** {appt['patient_id']}")
                            st.write(f"**Doctor:** {appt['doctor_id']}")
                            st.write(f"**Status:** {appt['status']}")
                else:
                    st.error(msg)
        
        elif view_option == "By Appointment ID":
            appt_id = st.text_input("Appointment ID", key="view_appt_id")
            if st.button("Search"):
                if appt_id:
                    success, msg, appt = manager.view_appointment_nurse(appointment_id=appt_id)
                    if success:
                        st.success(msg)
                        st.json(appt)
                    else:
                        st.error(msg)
        
        elif view_option == "By Patient ID":
            patient_id = st.text_input("Patient ID", key="view_patient_appts")
            if st.button("Search"):
                if patient_id:
                    success, msg, appts = manager.view_appointment_nurse(patient_id=patient_id)
                    if success:
                        st.success(msg)
                        for appt in appts:
                            with st.expander(f"Appointment {appt['appt_id']} - {appt['date']} {appt['time']}"):
                                st.write(f"**Doctor:** {appt['doctor_id']}")
                                st.write(f"**Status:** {appt['status']}")
                                st.write(f"**Remark:** {appt['remark']}")
                    else:
                        st.error(msg)
        
        elif view_option == "By Date":
            date_query = st.date_input("Select Date", value=datetime.date.today())
            if st.button("Search"):
                date_str = date_query.strftime("%Y-%m-%d")
                success, msg, results = manager.search_appointments_by_date(date_str)
                if success:
                    st.success(msg)
                    for appt in results:
                        with st.expander(f"Appointment {appt['appt_id']} - {appt['time']}"):
                            st.write(f"**Patient ID:** {appt['patient_id']}")
                            st.write(f"**Doctor ID:** {appt['doctor_id']}")
                            st.write(f"**Status:** {appt['status']}")
                else:
                    st.error(msg)
    
    #Create Appointment
    with tab2:
        with st.form("create_appointment_form"):
            st.subheader("➕ Create New Appointment")
            patient_id = st.text_input("Patient ID")
            doctor_id = st.text_input("Doctor ID")
            date = st.date_input("Appointment Date", min_value=datetime.date.today())
            time = st.time_input("Appointment Time")
            remark = st.text_area("Remark (Optional)")
            
            submitted = st.form_submit_button("Create Appointment", use_container_width=True)
            if submitted:
                if patient_id and doctor_id:
                    date_str = date.strftime("%Y-%m-%d")
                    time_str = time.strftime("%H:%M")
                    success, msg, appt_id = manager.create_appointment_nurse(
                        patient_id, doctor_id, date_str, time_str, remark
                    )
                    if success:
                        st.success(f"✅ {msg} (ID: {appt_id})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    #Update Appointment
    with tab3:
        with st.form("update_appointment_form"):
            st.subheader("💾 Update Appointment")
            appt_id_upd = st.text_input("Appointment ID")
            new_date = st.date_input("New Date (optional)", value=None)
            new_time = st.time_input("New Time (optional)", value=None)
            new_status = st.selectbox("New Status", ["", "scheduled", "completed", "cancelled", "no-show"])
            new_remark = st.text_area("New Remark (optional)")
            
            submitted = st.form_submit_button("Update Appointment", use_container_width=True)
            if submitted:
                if appt_id_upd:
                    date_str = new_date.strftime("%Y-%m-%d") if new_date else None
                    time_str = new_time.strftime("%H:%M") if new_time else None
                    status_str = new_status if new_status else None
                    
                    success, msg, _ = manager.update_appointment_nurse(
                        appt_id_upd, date_str, time_str, status_str, new_remark if new_remark else None
                    )
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please enter an Appointment ID")
    
    #Cancel Appointment
    with tab4:
        st.subheader("🗑️ Cancel Appointment")
        st.warning("This will mark the appointment as cancelled")
        
        appt_id_del = st.text_input("Appointment ID to Cancel")
        confirm_cancel = st.checkbox("I confirm I want to cancel this appointment")
        
        if st.button("Cancel Appointment", type="primary", use_container_width=True):
            if appt_id_del and confirm_cancel:
                success, msg, _ = manager.delete_appointment_nurse(appt_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("⚠️ Please enter an Appointment ID and confirm cancellation")


def patient_records_page(manager, username):
    """Patient Records Management Page"""
    st.header("📋 Patient Records Management")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "View Patient Details", 
        "Manage Records", 
        "View Records",
        "Update Record",
        "Delete Record"
    ])

    #View Patient Details
    with tab1:
        st.subheader("👤 View Patient Information")
        
        search_method = st.radio("Search by:", ["Patient ID", "Patient Name"], horizontal=True)
        
        if search_method == "Patient ID":
            patient_id = st.text_input("Enter Patient ID", key="view_patient_id")
            if st.button("🔍 Search Patient", key="search_patient_btn"):
                if patient_id:
                    success, msg, info = manager.view_patient_details_by_nurse(patient_id)
                    if success:
                        st.success(msg)
                        
                        # Display patient info
                        st.markdown("### Patient Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {info['name']}")
                            st.write(f"**Gender:** {info['gender']}")
                            st.write(f"**Email:** {info['email']}")
                        with col2:
                            st.write(f"**Contact:** {info['contact']}")
                            st.write(f"**Address:** {info['address']}")
                        
                        st.divider()
                        
                        # Display records
                        st.markdown("### Medical Records")
                        if info['records']:
                            for record in info['records']:
                                with st.expander(f"Record: {record['record_id']} - {record['timestamp']}"):
                                    st.write(f"**Conditions:** {record['conditions']}")
                                    st.write(f"**Medications:** {record['medications']}")
                                    st.write(f"**Remark:** {record['remark']}")
                        else:
                            st.info("No records found")
                        
                        st.divider()
                        
                        # Display remarks
                        st.markdown("### Patient Remarks")
                        if info['remarks']:
                            for remark in info['remarks']:
                                with st.expander(f"Remark: {remark['remark_id']} - {remark['type']} - {remark['timestamp']}"):
                                    st.write(f"**Doctor ID:** {remark['doctor_id']}")
                                    st.write(f"**Content:** {remark['content']}")
                        else:
                            st.info("No remarks found")
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a Patient ID")
        
        else:  
            patient_name = st.text_input("Enter Patient Name", key="search_patient_name")
            if st.button("🔍 Search", key="search_by_name_btn"):
                if patient_name:
                    success, msg, results = manager.search_patient_by_name(patient_name)
                    if success:
                        st.success(msg)
                        for patient in results:
                            with st.container():
                                st.markdown(f"### {patient['name']}")
                                st.write(f"**ID:** {patient['patient_id']}")
                                st.write(f"**Gender:** {patient['gender']}")
                                st.write(f"**Contact:** {patient['contact']}")
                                st.write(f"**Email:** {patient['email']}")
                                st.divider()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a name to search")

    #Create Record
    with tab2:
        with st.form("create_record_form"):
            st.markdown("### Create New Record")
            patient_id_rec = st.text_input("Patient ID", key="create_rec_pid")
            conditions = st.text_area("Conditions", key="create_conditions")
            medications = st.text_area("Medications", key="create_medications")
            remark = st.text_area("Remark (Optional)", key="create_rec_remark")
            
            submitted = st.form_submit_button("➕ Create Record", use_container_width=True)
            if submitted:
                if patient_id_rec and conditions and medications:
                    success, msg, record_id = manager.create_patient_record_nurse(
                        patient_id_rec, conditions, medications, remark
                    )
                    if success:
                        st.success(f"✅ {msg} (Record ID: {record_id})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    #View Records
    with tab3:
        patient_id_view = st.text_input("Enter Patient ID", key="view_rec_pid")
        if st.button("🔍 View Records", key="view_rec_btn"):
            if patient_id_view:
                success, msg, records = manager.view_patient_records_nurse(patient_id_view)
                if success:
                    st.success(msg)
                    for record in records:
                        with st.expander(f"Record: {record['record_id']} - {record['timestamp']}"):
                            st.write(f"**Conditions:** {record['conditions']}")
                            st.write(f"**Medications:** {record['medications']}")
                            st.write(f"**Remark:** {record['remark']}")
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a Patient ID")
    
    #Update Record
    with tab4:
        with st.form("update_record_form"):
            st.markdown("### Update Existing Record")
            record_id_upd = st.text_input("Record ID", key="upd_rec_id")
            conditions_upd = st.text_area("New Conditions (leave empty to keep current)", key="upd_conditions")
            medications_upd = st.text_area("New Medications (leave empty to keep current)", key="upd_medications")
            remark_upd = st.text_area("New Remark (leave empty to keep current)", key="upd_rec_remark")
            
            submitted = st.form_submit_button("💾 Update Record", use_container_width=True)
            if submitted:
                if record_id_upd:
                    success, msg, rid = manager.update_patient_record_nurse(
                        record_id_upd,
                        conditions=conditions_upd if conditions_upd else None,
                        medications=medications_upd if medications_upd else None,
                        remark=remark_upd if remark_upd else None
                    )
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please enter a Record ID")
    
    #Delete Record
    with tab5:
        st.markdown("### ⚠️ Delete Record")
        st.warning("This action cannot be undone!")
        
        record_id_del = st.text_input("Record ID to Delete", key="del_rec_id")
        confirm_delete = st.checkbox("I confirm I want to delete this record", key="confirm_del_rec")
        
        if st.button("🗑️ Delete Record", type="primary", use_container_width=True):
            if record_id_del and confirm_delete:
                success, msg, rid = manager.delete_patient_record_nurse(record_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("⚠️ Please enter a Record ID and confirm deletion")


def remarks_page(manager, username):
    """Remarks Management Page"""
    st.header("💬 Patient Remarks Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Add Remark",
        "View Remarks",
        "Update Remark", 
        "Delete Remark"
    ])
    
    #Add Remark
    with tab1:
        with st.form("add_remark_form"):
            st.markdown("### Add New Remark")
            patient_id_remark = st.text_input("Patient ID", key="add_rem_pid")
            remark_type = st.selectbox(
                "Remark Type", 
                ["mood", "pain_level", "general", "observation", "vital_signs", "medication_response"],
                key="remark_type"
            )
            remark_content = st.text_area("Remark Content", key="remark_content")
            
            submitted = st.form_submit_button("➕ Add Remark", use_container_width=True)
            if submitted:
                if patient_id_remark and remark_content:
                    success, msg, rid = manager.add_patient_remark_nurse(
                        patient_id_remark, username, remark_type, remark_content
                    )
                    if success:
                        st.success(f"✅ {msg} (Remark ID: {rid})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please fill in all fields")
    
    #View Remarks
    with tab2:
        st.subheader("👁️ View Patient Remarks")
        patient_id_remarks = st.text_input("Enter Patient ID", key="view_remarks_pid")
        if st.button("🔍 View Remarks", key="view_remarks_btn"):
            if patient_id_remarks:
                success, msg, remarks = manager.view_patient_remarks_nurse(patient_id_remarks)
                if success:
                    st.success(msg)
                    for remark in remarks:
                        with st.expander(f"Remark {remark['remark_id']} - {remark['type']} - {remark['timestamp']}"):
                            st.write(f"**Doctor ID:** {remark['doctor_id']}")
                            st.write(f"**Content:** {remark['content']}")
                            st.write(f"**Last Modified:** {remark['last_modified']}")
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a Patient ID")
    
    #Update Remark
    with tab3:
        with st.form("update_remark_form"):
            st.markdown("### Update Existing Remark")
            remark_id_upd = st.number_input("Remark ID", min_value=1, step=1, key="upd_rem_id")
            new_content = st.text_area("New Content", key="upd_rem_content")
            
            submitted = st.form_submit_button("💾 Update Remark", use_container_width=True)
            if submitted:
                if remark_id_upd and new_content:
                    success, msg, rid = manager.update_patient_remark_nurse(remark_id_upd, new_content)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please enter Remark ID and new content")
    
    #Delete Remark
    with tab4:
        st.markdown("### ⚠️ Delete Remark")
        st.warning("This will deactivate the remark")
        
        remark_id_del = st.number_input("Remark ID to Delete", min_value=1, step=1, key="del_rem_id")
        confirm_delete_rem = st.checkbox("I confirm I want to delete this remark", key="confirm_del_rem")
        
        if st.button("🗑️ Delete Remark", type="primary", use_container_width=True):
            if remark_id_del and confirm_delete_rem:
                success, msg, rid = manager.delete_patient_remark_nurse(remark_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("⚠️ Please enter a Remark ID and confirm deletion")


def nurse_page(nurse: NurseUser):
    global username
    username = st.session_state.username
    global manager
    manager = st.session_state.manager

    if not username:
        st.error("No user logged in")
        return

    tabs = ["Dashboard", "Profile", "Appointments", "Patient Records", "Remarks"]

    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page
    st.title(f"🏥 CareLog")
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Select", tabs, key="nurse_sidebar_radio")
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True, key="nurse_logout_btn")
    
    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Appointments":
        appointments_page(manager, username)
    elif option == "Patient Records":
        patient_records_page(manager, username)
    elif option == "Remarks":
        remarks_page(manager, username)
    

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True
