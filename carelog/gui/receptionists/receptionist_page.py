import streamlit as st

def dashboard():
    st.write("This is the Dashboard")

def patient_search_ui():
    st.subheader("Search Patients")
    manager = ReceptionistManager()

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

def receptionist_page(manager):
    # Variables
    username = st.session_state.get("username", "Unknown")
    # doctor = next((d for d in manager.doctos if d.username == username), None)
    tabs = ["Dashboard", "Patient Search", "Appointments", "Profile"]

    # Session state
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Sidebar
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)

    # Page design
    st.title(f"CareLog Dashboard - Welcome {username}")

    if option == "Dashboard":
        dashboard()
    elif option == "Patient Search":
        patient_search_ui()
    elif option == "Appointments":
        st.write("Appointments page coming soon...")
    elif option == "Profile":
        st.write("Profile page coming soon...")

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True