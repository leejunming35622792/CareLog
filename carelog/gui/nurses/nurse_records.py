import streamlit as st
from helper_manager.profile_manager import (search_patient_by_name, view_patient_details_by_nurse)
from app.user import User
from app.nurse import NurseUser

def patient_records_page(manager, username):
    nurse = NurseUser("", username, "", "", "", "", "", "", "", "", "", "", "")
    """Patient Records Management Page"""
    st.header("Patient Records Management 📋")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "View Patient Details", 
        "Manage Records", 
        "View Records",
        "Update Record",
        "Delete Record"
    ])

    #View Patient Details
    with tab1:
        st.subheader("View Patient Information 👤")
        st.info("To find a patient, enter patient ID or name.")
        
        search_method = st.radio("Search by:", ["Patient ID", "Patient Name"], horizontal=True)
        
        if search_method == "Patient ID":
            patient_id = st.text_input("Enter Patient ID", key="view_patient_id")
            if st.button("Search Patient 🔍", key="search_patient_btn"):
                if patient_id:
                    success, msg, info = view_patient_details_by_nurse(patient_id)
                    if success:
                        st.success(msg)
                        # Display patient info
                        if info is not None:
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
                            if info.get('records'):
                                for record in info['records']:
                                    with st.expander(f"Record: {record['record_id']} - {record['timestamp']}"):
                                        st.write(f"**Conditions:** {record['conditions']}")
                                        st.write(f"**Medications:** {record['medications']}")
                                        st.write(f"**Remark:** {record[4]}")
                            else:
                                st.info("No records found")
                            
                            st.divider()
                            
                            # Display remarks
                            st.markdown("### Patient Remarks")
                            if info.get('remarks'):
                                for remark in info['remarks']:
                                    with st.expander(f"Remark: {remark['remark_id']} - {remark['type']} - {remark['timestamp']}"):
                                        st.write(f"**Doctor ID:** {remark['doctor_id']}")
                                        st.write(f"**Content:** {remark['content']}")
                            else:
                                st.info("No remarks found")
                        else:
                            st.error("Patient information not found.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a Patient ID")
        
        else:  
            patient_name = st.text_input("Enter Patient Name", key="search_patient_name")
            if st.button("🔍 Search", key="search_by_name_btn"):
                if patient_name:
                    success, msg, results = search_patient_by_name(patient_name)
                    if success:
                        st.success(msg)
                        if results:
                            for patient in results:
                                with st.container():
                                    st.markdown(f"### {patient['name']}")
                                    st.write(f"**ID:** {patient['patient_id']}")
                                    st.write(f"**Gender:** {patient['gender']}")
                                    st.write(f"**Contact:** {patient['contact']}")
                                    st.write(f"**Email:** {patient['email']}")
                                    st.divider()
                        else:
                            st.info("No patients found.")
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
                    success, msg, record_id = nurse.create_patient_record(
                        patient_id_rec, conditions, medications, remark)
                    if success:
                        st.success(f"✅ {msg} (Record ID: {record_id})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please fill in all required fields")
    
    #View Records
    with tab3:
        patient_id_view = st.text_input("Enter Patient ID", key="view_rec_pid")
        if st.button("🔍 View Records", key="view_rec_btn"):
            if patient_id_view:
                success, msg, records = nurse.view_patient_records(patient_id_view)
                if success:
                    st.success(msg)
                    if records:
                        for record in records:
                            # If record is a dict, use keys; if list, use indices
                            if isinstance(record, dict):
                                with st.expander(f"Record: {record.get('record_id', '')} - {record.get('timestamp', '')}"):
                                    st.write(f"**Conditions:** {record.get('conditions', '')}")
                                    st.write(f"**Medications:** {record.get('medications', '')}")
                                    st.write(f"**Remark:** {record.get('remark', '')}")
                            elif isinstance(record, list):
                                # Assuming the order: [record_id, timestamp, conditions, medications, remark]
                                with st.expander(f"Record: {record[0]} - {record[1]}"):
                                    st.write(f"**Conditions:** {record[2]}")
                                    st.write(f"**Medications:** {record[3]}")
                                    st.write(f"**Remark:** {record[4]}")
                    else:
                        st.error("No record found")
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
            
            submitted = st.form_submit_button("Update Record", use_container_width=True)
            if submitted:
                if record_id_upd:
                    success, msg, rid = nurse.update_patient_record(
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
                    st.warning("Please enter a Record ID")
    
    #Delete Record
    with tab5:
        st.markdown("### 🗑️ Delete Record")
        st.warning("This action cannot be undone!")
        
        record_id_del = st.text_input("Record ID to Delete", key="del_rec_id")
        confirm_delete = st.checkbox("I confirm I want to delete this record", key="confirm_del_rec")
        
        if st.button("🗑️ Delete Record", type="primary", use_container_width=True):
            if record_id_del and confirm_delete:
                success, msg, rid = nurse.delete_patient_record(record_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter a Record ID and confirm deletion")