import streamlit as st
import datetime
from app.user import User

def profile_page(manager, username):
   # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # Variables
    nurse = next((n for n in manager.nurses if n.username == username), None)

    with st.form("update_nurse_profile"):
        # Page design
        if nurse.gender == "Male":
            disp = "Your Profile 👨"
        elif nurse.gender == "Female":
            disp = "Your Profile 👧"
        else:
            disp = "Your Profile 👥"
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>{disp}</h1>", unsafe_allow_html=True)
        st.divider()

        with st.container():
            st.markdown("### Personal Details")
            col1, col2 = st.columns([1, 1])
            with col1:
                new_name = st.text_input("Name", value=nurse.name)
                new_gender = st.text_input("Gender", value=nurse.gender)
                date_joined = datetime.datetime.fromisoformat(nurse.date_joined)
                st.text_input("Date Joined", value=date_joined, disabled=True)
            with col2:
                new_email = st.text_input("Email", value=nurse.email)
                new_contact = st.text_input("Contact", value=nurse.contact_num)
                new_email = st.text_input("Address", value=nurse.address)

        st.markdown("### Professional Details")
        col3, col4 = st.columns(2)
        with col3:
            new_department = st.text_input("Department", value=nurse.department)
        with col4:
            new_speciality = st.text_input("Speciality", value=nurse.speciality)

        st.markdown("")
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            pass

