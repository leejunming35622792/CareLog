import streamlit as st
from app.nurse import NurseUser
from gui.nurses.nurse_dashboard import dashboard
from gui.nurses.nurse_profile import profile_page


def patient_records_page():
    st.header("Patient Records & remarks")

    tab1, tab2 = st.tabs(["View Patient Details", "Add Remark"])

    with tab1:
        patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)
        if st.button("Search Patient"):
            success, msg, info = manager.view_patient_details_by_nurse(patient_id)
            if success:
                st.success(msg)
                st.json(info)
            else:
                st.error(msg)

    with tab2:
        with st.form("add_remark_form"):
            patient_id_remark = st.number_input("Patient ID", min_value=1, step=1, key="nurse_patient_remark")
            remark_type = st.selectbox("Remark Type", ["mood", "pain_level", "general", "observation"], key="remark_type")
            remark_content = st.text_area("Remark Content", key="remark_content")
            submitted = st.form_submit_button("Add Remark")
            if submitted:
                success, msg, rid = manager.add_patient_remark_nurse(
                    patient_id_remark, username, remark_type, remark_content
                )
                if success:
                    st.success(f"{msg} (Remark ID: {rid})")
                else:
                    st.error(msg)

def nurse_page(nurse: NurseUser):
    global username
    username = st.session_state.username
    global manager
    manager = st.session_state.manager

    if not username:
        st.error("No user logged in")
        return

    tabs = ["Dashboard", "Profile", "Patient Records"]

    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.title(f"🏥 CareLog")
    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    option = st.sidebar.radio("Select", tabs, key="nurse_sidebar_radio")
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True, key="nurse_logout_btn")
    
    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient Records":
        patient_records_page()
    
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True