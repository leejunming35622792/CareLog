import streamlit as st
import time
import datetime
import re
import bcrypt
from helper_manager.password_utils import (is_hashed, check_password)
from app.user import User
from helper_manager.profile_manager import find_age
from helper_manager.unchanged import unchanged_to_none

def profile(Manager):
    # Variables
    manager = st.session_state.manager
    username = st.session_state.username

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # User profile
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

        st.info("💡 Your existing details are shown below. To update your profile, simply edit any information you wish to change and click **'Save Changes'**.")

        # layout with columns
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", value=f"@{patient.username}", disabled=True)
            # new_password = st.text_input("Password", value=patient.password, type="password", disabled=True)
            new_name = st.text_input("Name", value=patient.name).title()
            new_gender = st.selectbox(
                "Gender", 
                ["Male", "Female", "Other"], 
                index=["Male", "Female", "Other"].index(patient.gender) if patient.gender in ["Male", "Female", "Other"] else 2)
            
            col3, col4 = st.columns(2)
            with col3:
                patient_bday = datetime.datetime.fromisoformat(patient.bday)
                new_bday = st.date_input("Date of Birth", value=patient_bday, min_value="1900-01-01")
            with col4:
                # find age
                age = find_age(patient.bday)
                # display age
                new_age = st.text_input("Age", value=str(age), disabled=True)

        with col2:
            new_address = st.text_area("Address", value=patient.address).title()
            new_email = st.text_input("Email", value=patient.email)
            new_contact_num = st.text_input("Contact Number", value=patient.contact_num, help="+6012-3456789")
            new_date_joined = st.text_input("Date Joined", value=patient.date_joined, disabled=True)

        new_remark = st.text_area("Remark", value=patient.p_remark)

        # save button
        button = st.form_submit_button("Save Changes")

        if button:
            errors = []

            # username validation
            all_usernames = [p.username for p in manager.patients if p.username != patient.username]
            if not new_username:
                errors.append("Username cannot be empty!")
            elif new_username in all_usernames:
                errors.append("Username has been taken!")

            # password validation
            # if patient.password != new_password:
            #     if len(new_password) < 8:
            #         errors.append("Password must be at least 8 characters!")
            #     if not any(c.isupper() for c in new_password):
            #         errors.append("Password must contain at least 1 uppercase letter.")

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
            # birthday validation
            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_name = unchanged_to_none(new_name, patient.name)
                new_bday = unchanged_to_none(new_bday.isoformat(), patient.bday)
                new_gender = unchanged_to_none(new_gender, patient.gender)
                new_address = unchanged_to_none(new_address, patient.address)
                new_email = unchanged_to_none(new_email, patient.email)
                new_contact_num = unchanged_to_none(new_contact_num, patient.contact_num)
                new_remark = unchanged_to_none(new_remark, patient.p_remark)

                result, msg, updated_field = User.update_profile(manager, patient.p_id, "patient", username, None, new_name, new_bday, new_gender, new_address, new_email, new_contact_num, new_remark, None, None)

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