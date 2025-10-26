import streamlit as st
import datetime
from helper_manager.appointment_manager import AppointmentManager
from helper_manager.profile_manager import (view_patient_details_by_nurse, search_patient_by_name)

appt_manager = AppointmentManager(st.session_state.manager)

def dashboard(manager, username):
    # Find current nurse user
    nurse = next((n for n in manager.nurses if n.username == username), None)
    if nurse is None:
        st.error("Nurse not found.")
        return

    # Page design
    st.markdown("<h1 style='text-align: center;'>Welcome to CareLog!</h1>", unsafe_allow_html=True)
    st.image("img/dashboard.png")
    st.divider()

    # --- Dashboard ---
    st.header("Dashboard Overview 🎗️")
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Nurse ID", nurse.n_id)
    with col2: st.metric("Department", nurse.department if nurse.department else "Not Set")
    with col3: st.metric("Speciality", nurse.speciality if nurse.speciality else "Not Set")
    st.divider()

    # --- Search Patient ---
    st.header("Quick Search 🔍")
    st.write("")
    with st.expander("Filter Patients", expanded=True):
        search_type = st.radio("Search By:", ["Patient ID", "Name"], horizontal=True)

        if search_type == "Patient ID":
            query = st.text_input("Enter search value", value="P000X")
        else:
            query = st.text_input("Enter search value", placeholder="")

        if st.button("Search🔍", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a value to search ⚠️")
            else:
                if search_type == "Patient ID":
                    try:
                        patient_id = int(query) if query.isdigit() else query
                        success, msg, info = view_patient_details_by_nurse(patient_id)
                    except ValueError:
                        st.error("Invalid Patient ID format")
                        return
                else:
                    success, msg, info = search_patient_by_name("nurse", username, query)

                if success:
                    st.success(msg)
                    st.divider()
                    if isinstance(info, list):
                        for patient in info:
                            with st.container():
                                st.markdown(f"<h1 style='font-size:200%'>🧍{patient['name']} (ID: {patient['patient_id']})</h1>", unsafe_allow_html=True)
                                st.markdown(f"<span style='font-size:200%'>💌 </span><span style='font-size:100%'>{patient['email']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span style='font-size:200%'>📞 </span><span style='font-size:100%'>{patient['contact']}</span>", unsafe_allow_html=True)
                                st.markdown("_____")
                    else:
                        st.json(info)
                else:
                    st.error(msg)
    
    st.divider()

    # --- Appointments ---
    st.header("Today's Appointments 📆")
    today = datetime.date.today()
    success, msg, appointments = appt_manager.list(manager, "nurse", username, scope="own", upcoming_only=True, date=today, status=None, patient_id=None, doctor_id=None, appt_id=None)

    st.info(appointments)

    if success and appointments:
        disp1, disp2, disp3 = st.columns(3)
        with disp1:
            confirm_appt = [appt for appt in appointments if appt["status"] == "Booked"]
            st.metric("Today", f"{len(confirm_appt)} appointments", "Confirm Booked", "normal")
        with disp2:
            this_hour_appt = [appt for appt in appointments if appt["time"][1:3] == datetime.datetime.now().hour]
            st.metric("This Hour", f"{len(this_hour_appt)} appointments")
        with disp3:
            pass
        st.divider()
        for appt in appointments:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**Patient:** {appt['patient_id']}")
                with col2:
                    st.write(f"**Doctor:** {appt['doctor_id']}")
                with col3:
                    st.write(f"**Time** {appt['time']}")
                with col4:
                    status_color = {
                        "scheduled": "🟢",
                        "completed": "🔵",
                        "cancelled": "🔴",
                        "no-show": "🟡"
                    }
                    st.write(f"{status_color.get(appt['status'], '⚪️')} {appt['status']}")
                st.divider()
    else:
        st.info("No appointments scheduled for today")

        st.divider()

        st.header("Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_patients = len(manager.patients)
            st.metric("Total Patients", total_patients)
    
        with col2:
            active_appts = len([a for a in manager.appointments if a.status == "scheduled"])
            st.metric("Active Appointments", active_appts)

        with col3:
            total_remarks = len([r for r in manager.remarks if r.is_active])
            st.metric("Active Remarks", total_remarks)
