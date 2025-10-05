import streamlit as st

def dashboard(manager, username):
    st.divider()
    st.header("Dashboard Overview")
    nurse = next((n for n in manager.nurses if n.username == username), None)

    col1, col2, col3 = st.columns(3)

    with col1: st.metric("Nurse ID", nurse.n_id)
    with col2: st.metric("Department", nurse.department if nurse.department else "Not Set")
    with col3: st.metric("Speciality", nurse.speciality if nurse.department else "Not Set")

    st.divider()

    st.header("Quick Search")
    st.info("TODO: Filter button, appt, remark")

    st.divider()