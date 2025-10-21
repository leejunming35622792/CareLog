import streamlit as st
import datetime
from helper_manager.appointment_manager import AppointmentManager

appt_manager = AppointmentManager(st.session_state.manager)

def appointments_page(manager, username):
    """Appointments Management Page"""
    # Page design
    st.header("Appointments Management 📅")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "View Appointments",
        "Create Appointment", 
        "Update Appointment",
        "Cancel Appointment"
    ])
    
    #View Appointments
    with tab1:
        st.subheader("View Appointments 🔍")
        view_option = st.radio("View by:", ["All Appointments", "By Appointment ID", "By Patient ID", "By Date"], horizontal=True)
        
        if view_option == "All Appointments":
            if st.button("Show All Appointments"):
                success, msg, appts = appt_manager.view_appointment_nurse()
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
                    success, msg, appt = appt_manager.view_appointment_nurse(appointment_id=appt_id)
                    if success:
                        st.success(msg)
                        st.json(appt)
                    else:
                        st.error(msg)
        
        elif view_option == "By Patient ID":
            patient_id = st.text_input("Patient ID", key="view_patient_appts")
            if st.button("Search"):
                if patient_id:
                    success, msg, appts = appt_manager.view_appointment_nurse(patient_id=patient_id)
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
                success, msg, results = appt_manager.search_appointments_by_date(date_str)
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
            st.subheader("Create New Appointment")
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
                    success, msg, appt_id = appt_manager.create_appointment_nurse(
                        patient_id, doctor_id, date_str, time_str, remark
                    )
                    if success:
                        st.success(f"✅ {msg} (ID: {appt_id})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please fill in all required fields")
    
    #Update Appointment
    with tab3:
        with st.form("update_appointment_form"):
            st.subheader("Update Appointment")
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
                    
                    success, msg, _ = appt_manager.update_appointment_nurse(
                        appt_id_upd, date_str, time_str, status_str, new_remark if new_remark else None
                    )
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please enter an Appointment ID")
    
    #Cancel Appointment
    with tab4:
        st.subheader("❌Cancel Appointment")
        st.warning("This will mark the appointment as cancelled")
        
        appt_id_del = st.text_input("Appointment ID to Cancel")
        confirm_cancel = st.checkbox("I confirm I want to cancel this appointment")
        
        if st.button("Cancel Appointment", type="primary", use_container_width=True):
            if appt_id_del and confirm_cancel:
                success, msg, _ = appt_manager.delete_appointment_nurse(appt_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter an Appointment ID and confirm cancellation")
