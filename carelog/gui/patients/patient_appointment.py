import streamlit as st
import time
import pandas as pd

def appointment(manager):
    # Page design
    st.title("CareLog - We are here for you!")

    # Variables
    tabs = ["Book Appointment", "View Appointments"]
    status_type = ["Pending", "Booked", "Reschedules", "Cancelled"]
    errors = []
    username = st.session_state.username
    patient = next((p for p in manager.patients if p.username == username), None)
    doctor_list = {d.d_id:d.name for d in manager.doctors}

    tab1, tab2 = st.tabs(tabs)

    with tab1:
        
            # Page Design
            # st.subheader("Book Appointment")
            st.markdown("### 🗓️ Book a New Appointment")
            st.markdown("Please provide the details below to schedule your hospital visit.\n")
            st.divider()

            # Doctor selection
            doctor_id = {f"{d.d_id} - {d.name}": d.d_id for d in manager.doctors}
            if not doctor_id:
                st.warning("No doctors found!")
            else:
                with st.form("appt_form"):
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
                            manager.add_appointments(p_id, d_id, str(appt_date), str(appt_time), appt_remark)
                            with st.spinner("Submitting request..."):
                                time.sleep(1)
                            manager.save()
         
    with tab2:
        # Page design
        # st.subheader("View Appointments"
        st.markdown("### 📋 View Your Appointments\nSelect one of your appointments from the list below to see the details.")
        st.divider()

        appt_id = {f"Appointment {appt.appt_id} - {doctor_list[appt.doctor]}":appt.appt_id for appt in manager.appointments if str(appt.patient) == str(patient.p_id)}

        if not appt_id:
            st.warning("No appointments found!")
            
        else:
            with st.form("view-appt-form", clear_on_submit=False):
                choose_appt = st.selectbox("Select Appointments", appt_id.keys())
                appt_id = appt_id[choose_appt]
                appt = manager.search_appt(appt_id)
                search_button = st.form_submit_button("Search Appointment")

                if search_button:
                    appt_df = pd.Series(appt).to_frame("")
                    st.dataframe(appt_df)
