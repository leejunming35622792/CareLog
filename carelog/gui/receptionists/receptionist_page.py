import streamlit as st
from app.receptionist import ReceptionistUser as manager

def receptionist_page(manager):
    st.title("Receptionist Dashboard")
    tabs = ["Dashboard", "Patient Search", "Appointments", "Profile"]

    # Sidebar
    username = st.session_state.get("username", "Receptionist")
    st.sidebar.title(f"Welcome, {username}")
    option = st.sidebar.radio("Navigation", tabs)
    st.sidebar.button("Logout", on_click=logout)

    receptionist = next((r for r in manager.receptionists if r.username == username), None)

    if option == "Dashboard":
        dashboard(username)
    elif option == "Patient Search":
        patient_search_ui()
    elif option == "Appointments":
        tab1, tab2, tab3 = st.tabs(["Create Appointment", "View Appointments", "Update Status"])

        with tab1:
            st.subheader("Create New Appointment")
            patient_id = st.selectbox("Select Patient", [p.p_id for p in manager.patients])
            doctor_id = st.selectbox("Select Doctor", [d.d_id for d in manager.doctors])
            date = st.date_input("Appointment Date")
            time_ = st.time_input("Appointment Time")

            if st.button("Create Appointment"):
                success, message, _ = receptionist.create_appointment(patient_id, doctor_id, date.isoformat(), str(time_))
                if success:
                    st.success(message)
                else:
                    st.error(message)

        with tab2:
            st.subheader("All Appointments")
            if manager.appointments:
                for a in manager.appointments:
                    st.write(f"**{a['appt_id']}** - {a['patient_id']} with {a['doctor_id']} on {a['date']} at {a['time']} ({a['status']})")
            else:
                st.info("No appointments found.")

        with tab3:
            st.subheader("Update Appointment Status")
            appt_id = st.text_input("Enter Appointment ID")
            new_status = st.selectbox("New Status", ["Scheduled", "Completed", "Cancelled"])
            if st.button("Update Status"):
                success, message = receptionist.update_appointment_status(appt_id, new_status)
                if success:
                    st.success(message)
                else:
                    st.error(message)
                    
    elif option == "Profile":
        st.write("Profile page coming soon...")

def dashboard(username):
    st.subheader("Dashboard Overview")
    st.write(f"Logged in as: **{username}**")
    st.metric("Total Patients", len(manager.patients))
    st.metric("Total Appointments", len(manager.appointments))

# TODO: Already implemented receptionist.py, will redo this
def patient_search_ui():
    st.subheader("Search Patients")

    # Search bar
    query = st.text_input("Enter name, patient ID, email or contact: ")
    if query:
        results = manager.search_patients(query)
        if results:
            st.success(f"Found {len(results)} patients.")
            for p in results:
                with st.expander(f"{p.name} ({p.p_id})"):
                    st.write(f"**Gender:** {p.gender}")
                    st.write(f"**Email:** {p.email}")
                    st.write(f"**Contact:** {p.contact_num}")
                    st.write(f"**Address:** {p.address}")
                    st.write(f"**DOB:** {p.dob}")
                    st.write(f"**Remarks:** {p.remarks}")
                    st.divider()
        else:
            st.warning("No patients found.")
    else:
        st.info("Type something to search.")
    pass

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True