import streamlit as st
import datetime

def dashboard(manager, username):
    st.header("Nurse Dashboard Overview")

    password = st.session_state.get("password", "")
    success, message, profile = manager.view_nurse_details(username, password)

    if success:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Nurse ID", profile.get("staff_id", "N/A"))
        with col2: st.metric("Department", profile.get("department", "Not Set"))
        with col3: st.metric("Speciality", profile.get("speciality", "Not Set"))
    else:
        st.error(message)

def profile_page(manager, username):
    st.header("My Profile")

    password = st.session_state.get("password", "")
    success, message, profile = manager.view_nurse_details(username, password)

    if success:
        st.subheader("Current Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Name", value=profile.get("name", ""), disabled=True)
            st.text_input("Email", value=profile.get("email", ""), disabled=True)
            st.text_input("Gender", value=profile.get("gender", ""), disabled=True)
            st.text_input("Date Joined", value=profile.get("date_joined", ""), disabled=True)
        with col2:
            st.text_input("Contact", value=profile.get("contact_num", ""), diabled=True)
            st.text_input("Address", value=profile.get("address", ""), disabled=True)
            st.text_input("Department", value=profile.get("department", ""), disabled=True)
            st.text_input("Speciality", value=profile.get("speciality", ""), disabled=True)

        st.divider()
        st.subheader("Update Profile")

        with st.form("update_profile_form"):
            new_name = st.text_input("New Name (optional)")
            new_email = st.text_input("New Email (optional)")
            new_contact = st.text_input("New Contact Number (optional)")
            new_address = st.text_area("New Address (optional)")
            new_department = st.text_input("New Speciality (optional)")
            new_speciality = st.text_input("New Speciality (optional)")
            new_password = st.text_input("New Password (optional)", type="password")

            submitted = st.form_submit_button("Update Profile")
            if submitted:
                success = manager.update_nurse_details(
                    username=username,
                    new_password=new_password if new_password else None,
                    new_name=new_name if new_name else None,
                    new_address=new_address if new_address else None,
                    new_email=new_email if new_email else None,
                    new_contact_num=new_contact if new_contact else None,
                    new_department=new_department if new_department else None,
                    new_speciality=new_speciality if new_speciality else None,
                )
                if success:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Update failed")

    else:
        st.error(message)
def patient_records_page(manager, username):
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
            patient_id_remark = st.number_input("Patient ID", min_value=1, step=1)
            remark_type = st.selectbox("Remark Type", ["mood", "pain_level", "general", "observation"])
            remark_content = st.text_area("Remark Conetnt")
            submitted = st.form_submit_button("Add Remark")
            if submitted:
                success, msg, rid = manager.add_patient_remark_nurse(
                    patient_id_remark, username, remark_type, remark_content
                )
                if success:
                    st.success(f"{msg} (Remark ID: {rid})")
                else:
                    st.error(msg)

def nurse_page(Manager):
    global manager
    manager = Manager
    global username
    username = st.session_state.username

    if "password" not in st.session_state:
        st.session_state.password = st.session_state.get("password", "")

    tabs = ["Dashboard", "Profile", "Patient Records"]

    if "logout_trigerred" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    st.title(f"🏥 CareLog dashboard - Welcome Nurse {username}")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.radio("Select", tabs)
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)
    
    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient Records":
        patient_records_page(manager, username)
    
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True