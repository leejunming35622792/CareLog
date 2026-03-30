import streamlit as st
import time
import datetime 
from helper_manager.appointment_manager import AppointmentManager


def appointment(manager):
    # Session states
    if "success_msg" not in st.session_state:
        st.session_state.success_msg = ""

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # Variables
    manager = st.session_state.manager
    appt_manager = AppointmentManager(manager)
    tabs = ["Book Appointment", "View Appointments", "Edit Appointments"]
    doctors = {d.d_id:d.name for d in manager.doctors}
    status_type = ["Pending", "Booked", "Reschedules", "Cancelled"]
    errors = []
    username = st.session_state.username
    patient = next((p for p in manager.patients if p.username == username), None)
    doctor_list = {d.d_id:d.name for d in manager.doctors}

    tab1, tab2, tab3 = st.tabs(tabs)

    with tab1:
            # Doctor selection
            doctor_id = {f"{d.d_id} - {d.name}": d.d_id for d in manager.doctors}
            if not doctor_id:
                st.warning("No doctors found!")
            else:
                with st.form("appt_form", clear_on_submit=True):
                    # Page Design
                    st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Book a New Appointment 🗓️</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center; font-size: 100%; text-decoration: None'>Please provide the details below to schedule your hospital visit.</h1>", unsafe_allow_html=True)

                    st.divider()

                    # Patient info (locked)
                    if patient is not None:
                        p_id = st.text_input("Patient ID", value=patient.p_id, disabled=True)
                    else:
                        st.error("Patient not found! Please log in again.")
                        p_id = None

                    # Create input bow
                    doctor_disp = st.selectbox("Select Doctor", doctor_id.keys())
                    d_id = doctor_id[doctor_disp]

                    # Date and time in one row
                    col1, col2 = st.columns(2)
                    with col1:
                        appt_date = st.date_input("Appointment Date")
                    with col2:
                        appt_time = st.time_input("Appointment Time")

                    # Status & remarks in another row
                    col3, col4 = st.columns([1,2])
                    with col3:
                        appt_status = st.selectbox("Status", ["Scheduled"], disabled=True)
                    with col4:
                        appt_remark = st.text_area("Remarks", placeholder="Add any notes...", key="")

                    # Submit button
                    submitted = st.form_submit_button("Confirm Appointment")

                    if submitted:
                        if not d_id:
                            errors.append("Please choose a doctor!")
                        if not appt_date:
                            errors.append("Please choose a date!")
                        if not appt_time:
                            errors.append("Please choose a time!")

                        if errors:
                            for e in errors:
                                st.error(e)
                        else:
                            appt_date = appt_date.isoformat()
                            appt_time = appt_time.isoformat()
                            success, msg, appt = appt_manager.create("patient", username, p_id, d_id, appt_date, appt_time, appt_remark)
                            with st.spinner("Submitting request..."):
                                st.success(msg)
                                time.sleep(4)
                            st.session_state.success_msg = msg
                            manager.save()
                            st.rerun()

    with tab2:
        #display appointment details
        appt_id = {f"Appointment {appt.appt_id} - {doctor_list[appt.doctor]}":appt.appt_id for appt in manager.appointments if str(appt.patient) == str(patient.p_id)}

        if not appt_id:
            st.warning("No appointments found!")
            
        else:
            with st.form("view-appt-form", clear_on_submit=False):
                # page Design
                st.markdown(f"<h1 style='text-align: center; font-size: 200%'>View Your Appointments 🗓️</h1>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; font-size: 100%; text-decoration: None'> Select one of your appointments from the list below to see the details.</h1>", unsafe_allow_html=True)

                st.divider()

                # Iiput box
                st.header("Search 🔎")
                st.write("")
                choose_appt = st.selectbox("Select Appointments", appt_id.keys())
                appt_id = appt_id[choose_appt]

                # appointment in 'dict' type
                success, msg, appt_list = appt_manager.list(manager, "patient", username, scope="own", upcoming_only=False, date=None, status=None, patient_id=patient.p_id, doctor_id=None, appt_id=None)

                # display button
                search_button = st.form_submit_button("Search Appointment")

                # download button
                download_button = st.form_submit_button("Download Appointment")

                st.divider()

                if search_button:
                    # Find the selected appointment in the list
                    appt = next((a for a in appt_list if a["appt_id"] == appt_id), None)

                    st.header("Appointment 📄")
                    st.write("")
                    
                    if not appt:
                        st.warning("Appointment not found.")
                    else:
                        disp1, disp2, disp3 = st.columns(3)
                        with disp1:
                            st.metric("Appointment ID", appt["appt_id"])
                        with disp2:
                            st.metric("Patient ID", appt["patient_id"], delta=patient.name, delta_color="off")
                        with disp3:
                            doc_id_name = {d.d_id: d.name for d in manager.doctors}
                            appt_doc = appt["doctor_id"]
                            st.metric("Doctor ID", appt_doc, delta=doc_id_name.get(appt_doc, "Unknown"), delta_color="off")

                        disp4, disp5, disp6 = st.columns(3)
                        with disp4:
                            st.metric("Appointment Date", appt["date"])
                        with disp5:
                            st.metric("Appointment Time", appt["time"])
                        with disp6:
                            appt_status = appt["status"].title()
                            risk_color = {
                                "Scheduled": "green",
                                "Pending": "blue",
                                "Rescheduled": "yellow",
                                "Cancelled": "red"
                            }
                            color = risk_color.get(appt_status, "black")
                            st.markdown(f"**Appointment Status:**<br><span style='color:{color}; font-size:200%'><b>{appt_status}</b></span>", unsafe_allow_html=True)
                        
                        st.text_area("Remark", value=appt["remark"], disabled=True)
                # button performs a download of appointment report
                if download_button:
                    success, msg, appt_list = appt_manager.list(manager, "patient", username, scope="own", upcoming_only=False, date=None, status=None, patient_id=patient.p_id, doctor_id=None, appt_id=None)

                    appt = next((a for a in appt_list if a["appt_id"] == appt_id), None)

                    success, result, file_dir = appt_manager.export_report("patient", patient.username, appt_id)

                    if success:
                        st.session_state.success_msg = f"Successfully downloaded to '{file_dir}'"
                        st.rerun()
                    else:
                        st.warning(result)
    
    # the tab that edits the appointment of the self user patient 
    with tab3:
        # page Design
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Edit Your Appointments🖊️ </h1>", unsafe_allow_html=True)
        st.divider()

        if "edit" not in st.session_state:
            st.session_state.edit = ""

        if "cancel" not in st.session_state:
            st.session_state.cancel = ""

        patient_appt = [appt for appt in manager.appointments if appt.p_id == patient.p_id and appt.status.lower() != "cancelled"]
        # display appointment boxes
        if patient_appt:
            for i, appt in enumerate(patient_appt):
                with st.form(f"appt-box{i}"):
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.markdown(f"""
                        **Appointment ID:** {appt.appt_id}  
                        **Date:** {appt.date}  
                        **Time:** {appt.time}  
                        **Doctor:** {appt.d_id} - {doctors[appt.d_id]}  
                        **Remark:** {appt.remark}
                        """)

                    with col2:
                        appt_status = appt_status.title()
                        if appt.status == "Pending":
                            st.markdown(f"""
                            ### Status: :blue[{appt.status}]
                            """)
                        if appt.status in ["Booked", "Scheduled"] :
                            st.markdown(f"""
                            ### Status: :green[{appt.status}]
                            """)
                        if appt.status == "Rescheduled":
                            st.markdown(f"""
                            ### Status: :yellow[{appt.status}]
                            """)
                        if appt.status == "Cancelled":
                            st.markdown(f"""
                            ### Status: :red[{appt.status}]
                            """)
                    # form buttons
                    with col3:
                        edit_button = st.form_submit_button("Edit", key=f"edit-{appt.appt_id}", use_container_width=True)
                        cancel_button = st.form_submit_button("Cancel", key=f"cancel-{appt.appt_id}", use_container_width=True)

                        if edit_button:
                            st.session_state.edit = appt.appt_id
                            st.rerun()

                        if cancel_button:
                            st.session_state.cancel = appt.appt_id
                            st.rerun()
                    # confirm of cancellation
                    if st.session_state.cancel == appt.appt_id:
                        st.warning(f"⚠️ You are about to cancel Appointment {appt.appt_id}. This action cannot be undone.")
                        confirm_button = st.form_submit_button("Confirm Cancel", key=f"confirm-{appt.appt_id}", use_container_width=True)
                        if confirm_button:
                            success, msg, appt_idd = appt_manager.cancel(manager, "patient", username, appt.appt_id)
                            st.session_state.cancel = ""
                            st.session_state.success_msg = f"✅ Appointment {appt.appt_id} cancelled successfully!"
                            manager.save()
                            st.rerun()
                    
        else:
            st.warning("No appointments found!")
        # edit appointment form
        if "edit" in st.session_state and st.session_state.edit != "":
            # variables
            target_appt_id = st.session_state.edit
            target_appt = next((a for a in patient_appt if a.appt_id == target_appt_id), None)
            doctor_options = list(doctor_id.keys())
            current_doc_display = next((disp for disp, did in doctor_id.items() if did == target_appt.d_id), doctor_options[0])

            if target_appt:
                st.divider()
                st.markdown(f"### ✏️ Editing Appointment {target_appt.appt_id}")
                with st.form("edit-appt-form"):
                    doctor_disp = st.selectbox("Select Doctor", doctor_id.keys(), index=doctor_options.index(current_doc_display))
                    d_id = doctor_id[doctor_disp]
                    col1, col2 = st.columns(2)
                    with col1:
                        appt_date = st.date_input("Appointment Date", value=target_appt.date)
                    with col2:
                        appt_time = st.time_input("Appointment Time", value=target_appt.time)

                    appt_remark = st.text_area("Remarks", value=target_appt.remark)

                    submitted = st.form_submit_button("Save Changes")

                    if submitted:
                        result = appt_manager.update(manager, "patient", username, target_appt_id, date=appt_date.isoformat(), time=appt_time.isoformat(), doctor_id=d_id, status=target_appt.status, remark=appt_remark)
                        st.session_state.success_msg = f"Appointment {target_appt.appt_id} updated successfully!"
                        manager.save()
                        st.session_state.edit = ""  # reset
                        st.rerun()
    # display the success messages 
    if "success_msg" in st.session_state and st.session_state.success_msg != "" and st.session_state.success_msg != "[]" and st.session_state.success_msg != []:
        st.success(st.session_state.success_msg)
        time.sleep(1.5)
        st.session_state.success_msg = ""
