import streamlit as st
import datetime
import time
import os
# import backend functions from profile_manager and record_manager
from helper_manager.profile_manager import (
    search_patient_by_name, 
    view_patient_details_by_doctor
)

from helper_manager.record_manager import (
    add_record_doctor,
    view_patient_records_doctor, 
    delete_patient_record_doctor, 
    update_patient_record_doctor,
    print_record)

from helper_manager.unchanged import unchanged_to_none

# start of patient records page for doctors
def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    # variables 
    manager = st.session_state.manager
    current_doctor = next((d for d in manager.doctors if d.username == username), None)

    # page design
    st.title("Patient Management 😷")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add Records", "Update Record", "View Patient Details", "View Patient Records", "Delete Record"])

    # Add new records for patient 
    with tab1:
        st.subheader("Add Record 📃")
        patient_disp = {f"{p.p_id} - {p.name}": p.p_id for p in manager.patients}

        if not patient_disp:
            st.warning(" No patients found")
            st.stop()
        # assign medications form
        with st.form("assign_meds_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                pid = st.selectbox("Patient ID", patient_disp.keys(), key="assign_pid")
            # get doctor id    
            with col2:
                d_id = st.text_input("Doctor ID", current_doctor.d_id, disabled=True)
            # input fields for conditions, medications, prediction result, confidence score, and remarks
            col1, col2 = st.columns(2)
            with col1:
                conditions = st.text_area("Medical Conditions")
            # get medications input
            with col2:
                meds_input = st.text_area(
                "Medications (comma-separated or one per line)",
                height=100,
                )
            # shows prediction result and confidence score
            col3, col4 = st.columns(2)
            with col3:
                pred = ["Low risk", "Moderate risk", "High risk"]
                pred_result = st.selectbox("Prediction Result", pred)
            with col4:
                confidence_score = st.slider("Confidence Score", min_value=0.00, max_value=1.00, step=0.05)
            
            instructions = st.text_area("Remark (optional)", value="Before/ After Meal: \nDaily Dose: ")

            submit_assign = st.form_submit_button("Create Record")

            # process the form submission
            if submit_assign:
                meds_str = meds_input.replace("\n", ",")
                # validation checks
                if not pid:
                    st.error("Please choose a patient")
                if not conditions:
                    st.error("'Conditions' cannot be empty")
                if not pred_result:
                    st.error("'Prediction Result' cannot be empty")
                if not confidence_score:
                    st.error("'Confidence Score' cannot be empty")
                if not meds_str.strip():
                    st.error("Medications cannot be empty")
                else:
                    ok, msg, rec_id = add_record_doctor(
                        manager,
                        patient_id=patient_disp[pid],
                        doctor_id=d_id,
                        conditions= conditions,
                        medications=meds_str,
                        doctor_username=username,
                        pr_prediction_result=pred_result,
                        pr_confidence_score=confidence_score,
                        instructions=instructions,
                        new_record=True
                    )
                    
                    if ok:
                        with st.spinner("Processing"):
                            st.success(f"{msg}. Record ID: {rec_id}")
                            time.sleep(2)
                            manager.save()
                            st.rerun()
                    else:
                        st.error(msg)

    # Update existing patient records
    with tab2:
        st.subheader("Update Record 📝")

        records_disp = {f"{r.pr_record_id}": r for r in manager.records if r.d_id == current_doctor.d_id}

        if not records_disp:
            st.warning(f"⚠️ No records found for doctor {current_doctor.name}")
            st.stop()
            
        record_id_edit = st.selectbox("Select Record ID", options=records_disp.keys(), key="edit_rec_id")

        # Detect record change
        if "loaded_record_id" not in st.session_state or st.session_state.loaded_record_id != record_id_edit:
            st.session_state.loaded_record_id = record_id_edit
            # Remove old form inputs from session state
            for key in ["edit_rec_conditions", "edit_rec_medications", "edit_rec_billings"]:
                if key in st.session_state:
                    del st.session_state[key]

        current_record = records_disp[st.session_state.loaded_record_id]

        st.write(current_record.__dict__)

        with st.form("update-record-form"):
            # Display the form with current record details
            st.markdown(f"#### Record Information - {current_record.pr_record_id}")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Patient ID", current_record.p_id, disabled=True)
            with col2:
                st.text_input("Doctor ID", current_record. d_id, disabled=True)
            
            st.divider()
            st.markdown("#### Conditions")
            st.caption("Enter one per line. Use 'Name:Severity' (e.g., Hypertension:Moderate). If no severity, just write the name.")
            cond_text = st.text_area("", value=current_record.pr_conditions, height=120, label_visibility="hidden")

            st.divider()
            st.markdown("#### Medications")
            st.caption("Comma-separated list, e.g., Metformin, Lisinopril")
            meds_text = st.text_input("", value=", ".join(current_record.pr_medications) if isinstance(current_record.pr_medications, list) else str(current_record.pr_medications), label_visibility="hidden")
            
            st.divider()
            st.markdown("#### Others")
            col_a, col_b = st.columns(2)
            with col_a:
                pred = ["Low risk", "Moderate risk", "High risk"]
                previous_pred_result = current_record.pr_prediction_result
                pred_result = st.selectbox("Prediction Result", pred, index=pred.index(previous_pred_result) if previous_pred_result in pred else 0)
            with col_b:
                conf_score = st.slider("Confidence Score", min_value=0.0, step=0.01, max_value=1.0, value=current_record.pr_confidence_score)

            remark = st.text_area("Remark", value=current_record.pr_remark)

            billings_val = st.number_input("Billings", min_value=0.0, step=25.00, key="edit_rec_billings")

            # helper functions to parse conditions and medications
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
            
            # helper function to parse medications
            def _parse_meds(text: str):
                text = (text or "").strip()
                if not text:
                    return None
                items = [m.strip() for m in text.split(",") if m.strip()]
                return items if items else None
            
            update_button = st.form_submit_button("Update Record ", key="edit_rec_btn")

            if update_button:
                if not record_id_edit:
                    st.warning("Please select a Record ID")
                
                else:
                    conds = _parse_conditions(cond_text)
                    meds = _parse_meds(meds_text)   
                    billings = billings_val if billings_val is not None else None
                    pred = pred_result if (pred_result or pred_result == "") else None
                    conf = conf_score if conf_score is not None else None

                    conds = unchanged_to_none(conds, current_record.pr_conditions)
                    meds = unchanged_to_none(meds, current_record.pr_medications)
                    billings = unchanged_to_none(billings, current_record.pr_billings)
                    pred = unchanged_to_none(pred, current_record.pr_prediction_result)
                    conf = unchanged_to_none(conf, current_record.pr_confidence_score)
                    remark = unchanged_to_none(remark, current_record.pr_remark)

                    success, msg = update_patient_record_doctor(
                        manager, 
                        current_record.pr_record_id,
                        conditions=conds,
                        medications=meds,
                        billings=billings,
                        prediction_result=pred,
                        confidence_score=conf,
                    )

                    if success:
                        manager.save()
                        with st.spinner("Saving changes..."):
                            st.success(msg)
                            time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"{msg}")
    
    # View patient details
    with tab3:
        st.subheader("View Patient Details 😷")
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
        # display patient information                 
        else:
            def _search_by_name_cb():
                name = st.session_state.get("search_patient_name", "").strip()
                if not name:
                    st.session_state['search_results'] = []
                    st.session_state['search_msg'] = ""
                    st.session_state['search_success'] = False
                    return

                success, msg, results = search_patient_by_name("doctor", username, name)
                st.session_state['search_results'] = results or []
                st.session_state['search_msg'] = msg
                st.session_state['search_success'] = bool(success)

            patient_name = st.text_input("Enter Patient Name", key="search_patient_name", on_change=_search_by_name_cb)
            
            if st.button("Search", key="search_by_name_btn"):
                if not patient_name:
                    st.error("Please enter something")
                else:
                    _search_by_name_cb()
            st.divider()
            success = st.session_state.get('search_success', False)
            msg = st.session_state.get('search_msg', '')
            results = st.session_state.get('search_results', [])
            # display search results
            if not patient_name and not results:
                pass
            else:
                if success:
                    st.markdown("### Showing patients")
                    if msg:
                        st.success(msg)
                    if results:
                        for patient in results:
                            with st.container():
                                pid = patient.get('patient_id', patient.get('p_id', ''))
                                st.markdown(f"### {patient.get('name', 'N/A')}")

                                column1, column2 = st.columns(2)
                                with column1:
                                    st.write(f"**Name:** {patient.get('name', 'N/A')}")
                                    st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                                with column2:
                                    st.write(f"**ID:** {pid}")
                                    st.write(f"**Date of Birth:** {patient.get('bday', 'N/A')}")
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
    
    # View patient records
    with tab4:
        st.header("View Patient Records")
        patient_id_view = st.selectbox("Select Patient ID", options=[p.p_id for p in manager.patients], key="view_patient_id_2")
        if st.button("🔍 View Records", key="view_rec_btn"):
            if patient_id_view:
                success, msg, records = view_patient_records_doctor(patient_id_view)
                if success:
                    st.success(msg)
                    # display records
                    if records:
                        for num, record in enumerate(records):
                            timestamp = datetime.datetime.fromisoformat(record.get('timestamp', ''))

                            if isinstance(record, dict):
                                with st.expander(f"Record: {record.get('record_id', '')} - {timestamp}"):
                                    st.write(f"**Conditions:** {record.get('conditions', '')}")
                                    st.write(f"**Medications:** {record.get('medications', '')}")
                                    st.write(f"**Remark:** {record.get('remark', '')}")
                                    st.write("")
                                    
                                    if st.button("Download Record", key=f"download-{record.get('record_id')}"):
                                        download_record_id = record.get("record_id")
                                        
                                        download_record = next(
                                            r for r in manager.records
                                            if r.pr_record_id == download_record_id
                                        )

                                        success, msg, file_dir = temp_print_record(manager, current_doctor, download_record)

                                        if success:
                                            st.success(msg)
                                            st.info(f"Saved at: {file_dir}")
                                        else:
                                            st.error(msg)

                            # display record if it's a list            
                            elif isinstance(record, list):
                                with st.expander(f"Record: {record[0]} - {record[1]}"):
                                    st.write(f"**Conditions:** {record[2]}")
                                    st.write(f"**Medications:** {record[3]}")
                                    st.write(f"**Remark:** {record[4]}")

                                    download_button = st.button(f"Download Record - {record.pr_record_id}", key=record.get('record_id'))
                                    if download_button:
                                        print_record(manager, username, record.pr_record_id)
                    else:
                        st.error("No record found")
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a Patient ID") 
    
    # Delete patient record
    with tab5:
        st.subheader("Delete Patient Record")
        st.warning("Deleting a record is irreversible. Please proceed with caution.")
        options = [r.pr_record_id for r in manager.records]
        record_id_del = st.selectbox("Select Record ID", options=options, key="delete_rec_id")

        if st.button("Delete Record ", key="delete_rec_btn"):
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


def temp_print_record(manager, current_doctor, record):
    # from helper_manager.profile_manager import find_age

    folder_path = "record_report"
    os.makedirs(folder_path, exist_ok=True)
    file_dir = os.path.join(folder_path, f"{record.pr_record_id}.txt")

    patient = next((p for p in manager.patients if p.p_id == record.p_id), None)
    # doctor = next((d for d in manager.doctors if d.d_id == record.d_id), None)
    doctor = current_doctor

    with open(file_dir, 'w', encoding="utf-8") as f:
        f.write("+" + "=" * 70 + "+\n")
        f.write("|{:^70}|\n".format("CARELOG - MEDICAL RECORD REPORT"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Record ID", record.pr_record_id))
        f.write("| {:25} {:<43}|\n".format("Patient ID", getattr(patient, "p_id", "")))
        f.write("| {:25} {:<43}|\n".format("Patient Name", getattr(patient, "name", "")))
        # f.write("| {:25} {:<43}|\n".format("Patient Age", find_age(getattr(patient, "bday", ""))))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Doctor ID", getattr(doctor, "d_id", "")))
        f.write("| {:25} {:<43}|\n".format("Doctor Name", getattr(doctor, "name", "")))
        f.write("| {:25} {:<43}|\n".format("Department", getattr(doctor, "department", "")))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Date & Time", str(record.pr_timestamp)))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Conditions", record.pr_conditions))
        f.write("| {:25} {:<43}|\n".format("Medications", record.pr_medications))
        f.write("| {:25} {:<43}|\n".format("Billings (RM)", f"{record.pr_billings:.2f}"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Prediction Result", record.pr_prediction_result))
        f.write("| {:25} {:<43}|\n".format("Confidence Score", f"{record.pr_confidence_score:.2%}"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Remark", record.pr_remark))
        f.write("+" + "=" * 70 + "+\n")

    return True, "Record exported successfully.", file_dir