import streamlit as st

def dashboard(manager, username):
    st.divider()
    st.header("🩺 Nurse Dashboard Overview")

    nurse = next((n for n in manager.nurses if n.username == username), None)
    if nurse is None:
        st.error("Nurse not found.")
        return

    col1, col2, col3 = st.columns(3)

    with col1: st.metric("Nurse ID", nurse.n_id)
    with col2: st.metric("Department", nurse.department if nurse.department else "Not Set")
    with col3: st.metric("Speciality", nurse.speciality if nurse.speciality else "Not Set")

    st.divider()

    st.header("🔍Quick Search")
    with st.expander("Filter Patients", expanded=True):
        search_type = st.radio("Search By:", ["Patient ID", "Name"], horizontal=True)
        query = st.text_input("Enter search value")
        if st.button("🔍Search", use_container_width=True):
            if not query.strip():
                st.warning("⚠️Please enter a value to search")
            else:
                if search_type == "Patient ID":
                    try:
                        patient_id = int(query) if query.isdigit() else query
                        success, msg, info = manager.view_patient_details_by_nurse(patient_id)
                    except ValueError:
                        st.error("Invalid Patient ID format")
                        return
                else:
                    success, msg, info = manager.search_patient_by_name(query)

                if success:
                    st.success(msg)
                    if isinstance(info, list):
                        for patient in info:
                            with st.container():
                                st.markdown(f"**{patient['name']}** (ID: {patient['patient_id']})")
                                st.write(f"💌 {patient['email']} | 📞{patient['contact']}")
                                st.divider
                    else:
                        st.json(info)
                else:
                    st.error(msg)
    
    st.divider()

    st.header("📆Today's Appointments")
    success, msg, appointments = manager.get_todays_appointments()

    if success and appointments:
        st.success(msg)
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
