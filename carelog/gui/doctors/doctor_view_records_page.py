import streamlit as st

# details manager functions
from helper_manager.profile_manager import search_patient_by_name, view_patient_details_by_doctor

from helper_manager.record_manager import view_patient_records_doctor, delete_patient_record_doctor, update_patient_record_doctor

def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    st.header("Patient Records Management 📋")
    tab1, tab2, tab3, tab4 = st.tabs(["View Patient Details", "View Patient Records", "Update Record", "Delete Record"])

    # Tab 1: View Patient Details
    with tab1:
        st.subheader("View Patient Details")
        st.info("To find a patient, enter their Patient ID below or name.")
        search_method = st.radio("Search by:", ["Patient ID", "Patient Name"], horizontal=True)
        if search_method =="Patient ID":
            patient_id= st.selectbox("Select Patient ID", options=[p.p_id for p in manager.patients], key="view_patient_id")
            if st.button("Search Patient ", key="search_patient_btn"):
                if patient_id:
                    success, msg, info = view_patient_details_by_doctor(patient_id)
                    if success:
                        st.success(msg)
                        # Display only personal patient info (no medical details)
                        if info is not None:
                            st.markdown("### Patient Information")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Name:** {info.get('name', 'N/A')}")
                                st.write(f"**Gender:** {info.get('gender', 'N/A')}")
                            with col2:
                                st.write(f"**Patient ID:** {info.get('patient_id', 'N/A')}")
                                st.write(f"**Date of Birth:** {info.get('date_of_birth', 'N/A')}")


                            st.divider()
        else:
           
            def _search_by_name_cb():
                name = st.session_state.get("search_patient_name", "").strip()
                if not name:
                    # clear previous results
                    st.session_state['search_results'] = []
                    st.session_state['search_msg'] = ""
                    st.session_state['search_success'] = False
                    return

                success, msg, results = search_patient_by_name(name)
                st.session_state['search_results'] = results or []
                st.session_state['search_msg'] = msg
                st.session_state['search_success'] = bool(success)

            # text input: pressing Enter triggers on_change
            patient_name = st.text_input("Enter Patient Name", key="search_patient_name", on_change=_search_by_name_cb)

            # also allow button click to run the same callback
            if st.button("🔍 Search", key="search_by_name_btn"):
                _search_by_name_cb()

            # read results from session_state so both Enter and button share the same behavior
            success = st.session_state.get('search_success', False)
            msg = st.session_state.get('search_msg', '')
            results = st.session_state.get('search_results', [])

            if not patient_name and not results:
                # nothing to do yet
                pass
            else:
                if success:
                    if msg:
                        st.success(msg)
                    if results:
                        for patient in results:
                            # only show personal details in this tab; do not display medical info here
                            with st.container():
                                pid = patient.get('patient_id', patient.get('p_id', ''))
                                st.markdown(f"### {patient.get('name', 'N/A')}")
                                st.write(f"**ID:** {pid}")
                                st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                                # provide button to open records in Tab 2 (no records shown here)
                                if st.button("Open medical records in 'View Patient Records' tab", key=f"open_records_btn_name_{pid}"):
                                    st.session_state['view_patient_id_2'] = pid
                                    st.info("Patient selected for records. Please switch to the 'View Patient Records' tab to view medical records.")
                                st.divider()
                    else:
                        st.info("No patients found.")
                else:
                    # show message if present; if no message and no name, don't show
                    if msg:
                        st.error(msg)
                    elif not patient_name:
                        st.warning("Please enter a name to search")

    with tab2:
        st.subheader("View Patient Records")
        patient_id_view =st.selectbox("Select Patient ID", options=[p.p_id for p in manager.patients], key="view_patient_id_2")
        if st.button("🔍 View Records", key="view_rec_btn"):
            if patient_id_view:
                success, msg, records = view_patient_records_doctor(patient_id_view)
                if success:
                    st.success(msg)
                    if records:
                        for record in records:
                            if isinstance(record, dict):
                                with st.expander(f"Record: {record.get('record_id', '')} - {record.get('timestamp', '')}"):
                                    st.write(f"**Conditions:** {record.get('conditions', '')}")
                                    st.write(f"**Medications:** {record.get('medications', '')}")
                                    st.write(f"**Remark:** {record.get('remark', '')}")
                            elif isinstance(record, list):
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

    with tab3:
        st.subheader("Update Patient Record Remark")
        record_id_edit = st.selectbox("Select Record ID", options=[r.pr_record_id for r in manager.records], key="edit_rec_id")
        new_remark = st.text_area("Enter New Remark", key="edit_rec_remark")
        if st.button("Update Remark ✏️", key="edit_rec_btn"):
            if record_id_edit and new_remark:
                success, msg = update_patient_record_doctor(record_id_edit, new_remark)
                if success:
                    st.success(f" {msg}")
                else:
                    st.error(f" {msg}")
            else:
                st.warning("Please enter both Record ID and New Remark")
    with tab4:
        st.subheader("Delete Patient Record")
        st.warning("Deleting a record is irreversible. Please proceed with caution.")
        record_id_del = st.selectbox("Select Record ID", options=[r.pr_record_id for r in manager.records], key="delete_rec_id")
        if st.button("Delete Record 🗑️", key="delete_rec_btn"):
            if record_id_del:
                success, msg = delete_patient_record_doctor(record_id_del)
                if success:
                    st.success(f" {msg}")
                else:
                    st.error(f" {msg}")
            else:
                st.warning("Please enter a Record ID to delete")
