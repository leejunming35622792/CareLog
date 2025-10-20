import streamlit as st
import time
import datetime
from app.user import User
from helper_manager.profile_manager import find_age

def profile(Manager):
    # Variables
    manager = st.session_state.manager
    username = st.session_state.username

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    with st.form("profile-form"):
        # Find patient by username
        patient = next((p for p in manager.patients if p.username == username), None)
        if not patient:
            st.error("Unexpected Error!")
            return
        
        # Page design
        if patient.gender == "Male":
            disp = "Your Profile 👨"
        elif patient.gender == "Female":
            disp = "Your Profile 👧"
        else:
            disp = "Your Profile 👥"
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>{disp}</h1>", unsafe_allow_html=True)


        # Layout with columns
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username", value=f"@{patient.username}", disabled=True)
            new_password = st.text_input("Password", value=patient.password, type="password")
            new_name = st.text_input("Name", value=patient.name).title()

            col3, col4 = st.columns(2)
            with col3:
                new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                          index=["Male", "Female", "Other"].index(patient.gender) if patient.gender in ["Male", "Female", "Other"] else 2)
            with col4:
                new_bday = st.date_input("Birthday", value=patient.bday)
                # Find age
                age = find_age(patient.bday)
                # Display age
                new_age = st.text_input("Age", value=str(age), disabled=True)

        with col2:
            new_address = st.text_area("Address", value=patient.address).title()
            new_email = st.text_input("Email", value=patient.email)
            new_contact_num = st.text_input("Contact Number", value=patient.contact_num)
            new_date_joined = st.text_input("Date Joined", value=patient.date_joined, disabled=True)

        new_remark = st.text_area("Remark", value=patient.p_remark)

        # Save button
        button = st.form_submit_button("Save Changes")

        if button:
            errors = []

            # Username validation
            all_usernames = [p.username for p in manager.patients if p.username != patient.username]
            if not new_username:
                errors.append("Username cannot be empty!")
            elif new_username in all_usernames:
                errors.append("Username has been taken!")

            # Password validation
            if patient.password != new_password:
                if len(new_password) < 8:
                    errors.append("Password must be at least 8 characters!")
                if not any(c.isupper() for c in new_password):
                    errors.append("Password must contain at least 1 uppercase letter.")

            # Name validation
            if not new_name.strip():
                errors.append("Name cannot be empty!")

            # Email validation (very basic check)
            if "@" not in new_email or "." not in new_email:
                errors.append("Invalid email address.")

            # Contact validation (digits only, min length check)
            if not new_contact_num.isdigit() or len(new_contact_num) < 8:
                errors.append("Contact number must be at least 8 digits and numeric.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_bday = new_bday.isoformat()

                result = User.update_profile(manager, username, new_password, new_name, new_bday, new_gender, new_address, new_email, new_contact_num, new_remark, None, None, None)
                with st.spinner("Saving changes..."):
                    time.sleep(1)
                if result:
                    manager.save()
                    st.toast("Successfully Updated!")
                    st.rerun()