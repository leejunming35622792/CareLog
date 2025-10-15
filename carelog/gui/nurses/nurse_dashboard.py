import streamlit as st

def dashboard(manager, username):
    st.divider()
    st.header("🩺 Nurse Dashboard Overview")

    nurse = next((n for n in manager.nurses if n.username == username), None)
    if nurse is None:
        st.error("Nurse not found.")

    col1, col2, col3 = st.columns(3)

    with col1: st.metric("Nurse ID", nurse.n_id)
    with col2: st.metric("Department", nurse.department if nurse.department else "Not Set")
    with col3: st.metric("Speciality", nurse.speciality if nurse.department else "Not Set")

    st.divider()

    st.header("🔍Quick Search")
    with st.enpander("Filter Patients"):
        search_type = st.radio("Search By:", ["Patient ID", "Name"], horizontal=True)
        query = st.text_input("Enter search value")
        if st.button("Search", user_container_width=True):
            if not query.strip():
                st.warning("Please enter a value to search")
            else:
                if search_type == "Patient ID" and query.isdigit():
                    success, msg, info = manager.view_patient_details_by_nurse(int(query))
                else:
                    success, msg, info = manager.search_patient_by_name(query)

                if success:
                    st.success(msg)
                    st.json(info)
                else:
                    st.error(msg)
    
    st.divider()

    st.header("📆Today's Appointments")

    st.divider()

