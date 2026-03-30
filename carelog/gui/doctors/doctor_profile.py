import streamlit as st
import time
import datetime
import re
import bcrypt
from helper_manager.password_utils import (is_hashed, check_password)
from app.user import User
from helper_manager.profile_manager import find_age
from helper_manager.unchanged import unchanged_to_none

def doctor_profile(Manager):
    # Variables
    manager = st.session_state.manager
    username = st.session_state.username

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # User profile
    with st.form("profile-form"):
        # Find doctor by username
        doctor = next((d for d in manager.doctors if d.username == username), None)
        if not doctor:
            st.error("Unexpected Error!")
            return
        
        # Page design
        if doctor.gender == "Male":
            disp = "Your Profile 👨"
        elif doctor.gender == "Female":
            disp = "Your Profile 👧"
        else:
            disp = "Your Profile 👥"
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>{disp}</h1>", unsafe_allow_html=True)

        st.info("💡 Your existing details are shown below. To update your profile, simply edit any information you wish to change and click **'Save Changes'**.")

        # layout with columns
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", value=f"@{doctor.username}", disabled=True)
            # new_password = st.text_input("Password", value=doctor.password, type="password", disabled=True)
            new_name = st.text_input("Name", value=doctor.name).title()
            new_gender = st.selectbox(
                "Gender", 
                ["Male", "Female", "Other"], 
                index=["Male", "Female", "Other"].index(doctor.gender) if doctor.gender in ["Male", "Female", "Other"] else 2)
            
            col3, col4 = st.columns(2)
            with col3:
                doctor_bday = datetime.datetime.fromisoformat(doctor.bday)
                new_bday = st.date_input("Date of Birth", value=doctor_bday, min_value="1900-01-01")
            with col4:
                age = find_age(doctor.bday)
                new_age = st.text_input("Age", value=str(age), disabled=True)

        with col2:
            new_address = st.text_area("Address", value=doctor.address).title()
            new_email = st.text_input("Email", value=doctor.email)
            new_contact_num = st.text_input("Contact Number", value=doctor.contact_num, help="+6012-3456789")
            new_date_joined = st.text_input("Date Joined", value=doctor.date_joined, disabled=True)

        new_speciality = st.text_input("Speciality", value=doctor.speciality).capitalize()
        new_department = st.text_input("Department", value=doctor.department).capitalize()

        # Save button
        button = st.form_submit_button("Save Changes")

        if button:
            errors = []

            # Username validation
            all_usernames = [d.username for d in manager.doctors if d.username != doctor.username]
            if not new_username:
                errors.append("Username cannot be empty!")
            elif new_username in all_usernames:
                errors.append("Username has been taken!")

            # Name validation
            if not new_name.strip():
                errors.append("Name cannot be empty!")

            # Email validation (very basic check)
            if "@" not in new_email or "." not in new_email:
                errors.append("Invalid email address.")

            # Contact number validation
            contact_num_format = r"^\+601[0-9]-?[0-9]{7,8}$"
            if not re.match(contact_num_format, new_contact_num):
                errors.append("Contact number is invalid - please include '+60' and '-'")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_name = unchanged_to_none(new_name, doctor.name)
                new_bday = unchanged_to_none(new_bday.isoformat(), doctor.bday)
                new_gender = unchanged_to_none(new_gender, doctor.gender)
                new_address = unchanged_to_none(new_address, doctor.address)
                new_email = unchanged_to_none(new_email, doctor.email)
                new_contact_num = unchanged_to_none(new_contact_num, doctor.contact_num)
                new_speciality = unchanged_to_none(new_speciality, doctor.speciality)
                new_department = unchanged_to_none(new_department, doctor.department)

                result, msg, updated_field = User.update_profile(manager, doctor.d_id, "doctor", username, None, new_name, new_bday, new_gender, new_address, new_email, new_contact_num, None, new_department, new_speciality)

                if result:
                    if len(updated_field) == 0:
                        success_msg = f"No changes made!"
                        st.success(success_msg)
                    else:
                        with st.spinner("Saving changes..."):
                            if len(updated_field) == 1:
                                success_msg = f"{", ".join(updated_field)} is successfully updated!".capitalize()
                            else:
                                success_msg = f"{", ".join(updated_field)} are successfully updated!".capitalize()
                            st.success(success_msg)
                            time.sleep(3)

                            manager.save()
                            st.session_state.success_msg = msg
                            st.rerun()

