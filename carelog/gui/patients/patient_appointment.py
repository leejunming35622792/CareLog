import streamlit as st
import time
import pandas as pd
from helper_manager.appointment_manager import AppointmentManager

manager = st.session_state.manager
appt_manager = AppointmentManager(manager)

def appointment(manager):
    # Session states
    if "success_msg" not in st.session_state:
        st.session_state.success_msg = ""

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # Variables
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
                with st.form("appt_form"):
                    # Page Design
                    st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Book a New Appointment 🗓️</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center; font-size: 100%; text-decoration: None'>Please provide the details below to schedule your hospital visit.</h1>", unsafe_allow_html=True)

                    st.divider()

                    # Patient info (locked)
                    p_id = st.text_input("Patient ID", value=patient.p_id, disabled=True)

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
                        appt_status = st.selectbox("Status", ["Pending"], disabled=True)
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
                            appt_manager.add_appointments(p_id, d_id, str(appt_date), str(appt_time), appt_remark)
                            with st.spinner("Submitting request..."):
                                time.sleep(1)
                            manager.save()
         
    with tab2:
        # Display appointment id with doctor
        appt_id = {f"Appointment {appt.appt_id} - {doctor_list[appt.doctor]}":appt.appt_id for appt in manager.appointments if str(appt.patient) == str(patient.p_id)}

        if not appt_id:
            st.warning("No appointments found!")
            
        else:
            with st.form("view-appt-form", clear_on_submit=False):
                # Page Design
                st.markdown(f"<h1 style='text-align: center; font-size: 200%'>View Your Appointments 🗓️</h1>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; font-size: 100%; text-decoration: None'> Select one of your appointments from the list below to see the details.</h1>", unsafe_allow_html=True)

                st.divider()

                # Input box
                choose_appt = st.selectbox("Select Appointments", appt_id.keys())
                appt_id = appt_id[choose_appt]

                # Appointment in 'dict' type
                success, msg, appt = appt_manager.search_appt(appt_id)

                # Display button
                search_button = st.form_submit_button("Search Appointment")

                # Download button
                download_button = st.form_submit_button("Download Appointment")

                st.divider()

                if search_button:
                    disp1, disp2, disp3 = st.columns(3)
                    with disp1:
                        st.metric("Appointment ID", appt.get("Appointment ID"))
                    with disp2:
                        st.metric("Patient ID", appt["Patient ID"], delta=patient.name, delta_color="off")
                    with disp3:
                        doc_id_name = {d.d_id:d.name for d in manager.doctors}
                        appt_doc = appt["Doctor ID"]
                        st.metric("Doctor ID", appt["Doctor ID"], delta=f"{doc_id_name[appt_doc]}", delta_color="off")
                    disp4, disp5, disp6 = st.columns(3)
                    with disp4:
                        st.metric("Appointment Date", appt["Appointment Date"])
                    with disp5:
                        st.metric("Appointment Time", appt["Appointment Time"])
                    with disp6:
                        appt_status = appt["Appointment Status"]
                        risk_color = {
                            "Booked": "green",
                            "Pending": "blue",
                            "Rescheduled": "yellow",
                            "Cancelled": "red"
                        }

                        color = risk_color.get(appt_status, "black")
                        st.markdown(f"**Appointment Status:**<br><span style='color:{color};; font-size:200%'><b>{appt_status}</b></span>", unsafe_allow_html=True)
                    st.text_area("Remark", value=appt["Remark"], disabled=True)
                if download_button:
                    success, msg, appt = appt_manager.search_appt(appt_id)
                    result = appt_manager.print_appt(patient, appt)
                    if result:
                        st.session_state.success_msg = f"Successfully downloaded to {result}"
                        st.rerun()

    with tab3:
        # Page Design
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Edit Your Appointments🖊️ </h1>", unsafe_allow_html=True)
        st.divider()

        if "edit" not in st.session_state:
            st.session_state.edit = ""

        if "cancel" not in st.session_state:
            st.session_state.cancel = ""

        patient_appt = [appt for appt in manager.appointments if appt.p_id == patient.p_id]

        if patient_appt:
            for i, appt in enumerate(patient_appt):
                with st.form(f"appt-box{i}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"""
                        **Appointment ID:** {appt.appt_id}  
                        **Date:** {appt.date}  
                        **Time:** {appt.time}  
                        **Doctor:** {appt.d_id} - {doctors[appt.d_id]}  
                        **Remark:** {appt.remark}
                        """)

                    with col2:
                        if appt.status == "Pending":
                            st.markdown(f"""
                            ### Status: :blue[{appt.status}]
                            """)
                        if appt.status == "Booked":
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

                    with col3:
                        edit_button = st.form_submit_button("Edit", key=f"edit-{appt.appt_id}", use_container_width=True)
                        cancel_button = st.form_submit_button("Cancel", key=f"cancel-{appt.appt_id}", use_container_width=True)

                        if edit_button:
                            st.session_state.edit = appt.appt_id
                            st.rerun()
                        if cancel_button:
                            st.session_state.cancel = appt.appt_id
                            st.rerun()

                        if st.session_state.cancel:
                            confirm_delete_button = st.form_submit_button("Confirm Delete", use_container_width=True)

                            if confirm_delete_button != "":
                                manager.delete_appointments(st.session_state.cancel)
                                st.session_state.edit = ""
                                st.session_state.cancel = ""
                        
        else:
            st.warning("No appointments found!")

        st.divider()

        if "edit" in st.session_state and st.session_state.edit != "":
            # Variables
            target_appt_id = st.session_state.edit
            target_appt = next((a for a in patient_appt if a.appt_id == target_appt_id), None)
            doctor_options = list(doctor_id.keys())
            current_doc_display = next((disp for disp, did in doctor_id.items() if did == target_appt.d_id), doctor_options[0])


            if target_appt:
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
                        result = appt_manager.edit_appointments(target_appt_id, d_id, str(appt_date), str(appt_time), appt_remark)
                        st.session_state.success_msg = f"Appointment {target_appt.appt_id} updated successfully!"
                        manager.save()
                        st.session_state.edit = ""  # reset
                        st.rerun()

        st.divider()
        
    if "success_msg" in st.session_state and st.session_state.success_msg != "":
        st.success(st.session_state.success_msg)
        st.session_state.success_msg = ""