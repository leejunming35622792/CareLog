import streamlit as st
import datetime
import time
from app.user import User
from helper_manager.profile_manager import find_age

def profile_page(manager, username):
    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # Variables
    nurse = next((n for n in manager.nurses if n.username == username), None)

    with st.form("update_nurse_profile"):
        # Page design
        if nurse is not None:
            if nurse.gender == "Male":
                disp = "Your Profile 👨"
            elif nurse.gender == "Female":
                disp = "Your Profile 👧"
            else:
                disp = "Your Profile 👥"
        else:
            disp = "Nurse not found"
        st.markdown(f"<h1 style='text-align: center; font-size: 220%'>{disp}</h1>", unsafe_allow_html=True)
        st.divider()

        with st.container():
            st.markdown("### Login Credentials")
            disp1, disp2 = st.columns(2)
            with disp1:
                username = st.text_input("Username", value=nurse.username, disabled=True)
            with disp2:
                new_password = st.text_input("Password", value=nurse.password)

            st.markdown("### Personal Details")
            col1, col2 = st.columns([1, 1])
            with col1:
                new_name = st.text_input("Name", value=nurse.name if nurse else "")
                nurse_bday = datetime.datetime.fromisoformat(nurse.bday)
                new_bday = st.date_input("Birthday", value=nurse_bday)
                new_gender = st.text_input("Gender", value=nurse.gender if nurse else "")
                date_joined = datetime.datetime.fromisoformat(nurse.date_joined) if nurse and nurse.date_joined else ""
                st.text_input("Date Joined", value=date_joined, disabled=True)
            with col2:
                new_email = st.text_input("Email", value=nurse.email if nurse else "")
                # Find age
                age = find_age(nurse.bday)
                # Display age
                new_age = st.text_input("Age", value=str(age), disabled=True)
                new_contact = st.text_input("Contact", value=nurse.contact_num if nurse else "")
                new_address = st.text_input("Address", value=nurse.address if nurse else "")

        st.markdown("### Professional Details")
        col3, col4 = st.columns(2)
        with col3:
            new_department = st.text_input("Department", value=nurse.department if nurse else "")
        with col4:
            new_speciality = st.text_input("Speciality", value=nurse.speciality if nurse else "")

        st.markdown("")
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            new_name = new_name.title()
            new_bday = new_bday.isoformat()
            result, msg = User.update_profile(manager, nurse.n_id, "nurse", username, new_password, new_name, new_bday, new_gender, new_address, new_email, new_contact, None, new_department, new_speciality)
            with st.spinner("Saving changes..."):
                time.sleep(1)
            if result:
                manager.save()
                st.session_state.success_msg = msg
                st.rerun()
        