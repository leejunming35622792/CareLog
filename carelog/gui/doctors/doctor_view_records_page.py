import streamlit as st

# details manager functions
from helper_manager.profile_manager import search_patient_by_name, view_patient_details_by_doctor

from helper_manager.record_manager import view_patient_records_doctor, delete_patient_record_doctor, update_patient_record_doctor

def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    st.header("Patient Records Management 📋")
    tab1, tab2, tab3, tab4 = st.tabs(["View Patient Details", "View Patient Records", "Update Record", "Delete Record"])

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
                    st.session_state['search_results'] = []
                    st.session_state['search_msg'] = ""
                    st.session_state['search_success'] = False
                    return

                success, msg, results = search_patient_by_name(name)
                st.session_state['search_results'] = results or []
                st.session_state['search_msg'] = msg
                st.session_state['search_success'] = bool(success)

            patient_name = st.text_input("Enter Patient Name", key="search_patient_name", on_change=_search_by_name_cb)

            if st.button("🔍 Search", key="search_by_name_btn"):
                _search_by_name_cb()
            success = st.session_state.get('search_success', False)
            msg = st.session_state.get('search_msg', '')
            results = st.session_state.get('search_results', [])

            if not patient_name and not results:
                # wait
                pass
            else:
                if success:
                    if msg:
                        st.success(msg)
                    if results:
                        for patient in results:
                            with st.container():
                                pid = patient.get('patient_id', patient.get('p_id', ''))
                                st.markdown(f"### {patient.get('name', 'N/A')}")
                                st.write(f"**ID:** {pid}")
                                st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                                if st.button("Open medical records in 'View Patient Records' tab", key=f"open_records_btn_name_{pid}"):
                                    st.session_state['view_patient_id_2'] = pid
                                    st.info("Patient selected for records. Please switch to the 'View Patient Records' tab to view medical records.")
                                st.divider()
                    else:
                        st.info("No patients found.")
                else:
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
        st.subheader("Update Patient Record (Medical)")
        record_id_edit = st.selectbox("Select Record ID", options=[r.pr_record_id for r in manager.records], key="edit_rec_id")

        st.markdown("#### Conditions")
        st.caption("Enter one per line. Use 'Name:Severity' (e.g., Hypertension:Moderate). If no severity, just write the name.")
        cond_text = st.text_area("", key="edit_rec_conditions", height=120)

        st.markdown("#### Medications")
        st.caption("Comma-separated list, e.g., Metformin, Lisinopril")
        meds_text = st.text_input("", key="edit_rec_medications")

        col_a, col_b = st.columns(2)
        with col_a:
            billings_val = st.number_input("Billings", min_value=0.0, step=0.01, key="edit_rec_billings")
        with col_b:
            conf_score = st.number_input("Confidence Score", min_value=0.0, step=0.01, key="edit_rec_confidence")
        pred_result = st.text_input("Prediction Result", key="edit_rec_prediction")

        def _parse_conditions(text: str):
            text = (text or "").strip()
            if not text:
                return None
            result = {}
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    name, sev = line.split(":", 1)
                    result[name.strip()] = sev.strip()
                else:
                    result[line] = ""
            return result

        def _parse_meds(text: str):
            text = (text or "").strip()
            if not text:
                return None
            items = [m.strip() for m in text.split(",") if m.strip()]
            return items if items else None

        if st.button("Update Record ✏️", key="edit_rec_btn"):
            if not record_id_edit:
                st.warning("Please select a Record ID")
            else:
                conds = _parse_conditions(cond_text)
                meds = _parse_meds(meds_text)   
                billings = billings_val if billings_val is not None else None
                pred = pred_result if (pred_result or pred_result == "") else None
                conf = conf_score if conf_score is not None else None

                success, msg = update_patient_record_doctor(
                    manager,
                    record_id_edit,
                    conditions=conds,
                    medications=meds,
                    billings=billings,
                    prediction_result=pred,
                    confidence_score=conf,
                )
                if success:
                    st.success(f"{msg}")
                else:
                    st.error(f"{msg}")
    with tab4:
        st.subheader("Delete Patient Record")
        st.warning("Deleting a record is irreversible. Please proceed with caution.")
        options = [r.pr_record_id for r in manager.records]
        record_id_del = st.selectbox("Select Record ID", options=options, key="delete_rec_id")

        if st.button("Delete Record 🗑️", key="delete_rec_btn"):
            if record_id_del:
                st.session_state['pending_delete'] = record_id_del
            else:
                st.warning("Please select a Record ID to delete")

        pending = st.session_state.get('pending_delete')
        if pending:
            st.warning(f"Are you sure you want to permanently delete record {pending}? This action cannot be undone.")
            c1, c2 = st.columns(2)
            if c1.button("Confirm Delete", key="confirm_delete_btn"):
                with st.spinner("Deleting record..."):
                    success, msg, deleted_id = delete_patient_record_doctor(pending)
                if success:
                    try:
                        manager.records = [r for r in manager.records if r.pr_record_id != pending]
                    except Exception:
                        pass

                    if manager.records:
                        st.session_state['delete_rec_id'] = manager.records[0].pr_record_id
                    else:
                        st.session_state['delete_rec_id'] = ""

                    st.success(f"Record {deleted_id} deleted successfully")
                else:
                    st.error(msg)

                st.session_state.pop('pending_delete', None)

            if c2.button("Cancel", key="cancel_delete_btn"):
                st.info("Deletion cancelled")
                st.session_state.pop('pending_delete', None)
