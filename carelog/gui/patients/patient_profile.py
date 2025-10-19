import streamlit as st
import time
import datetime
from app.user import User

def profile(Manager):
    # Variables
    manager = st.session_state.manager
    username = st.session_state.username

    # Page design
    st.title("CareLog - About You")

    with st.form("profile-form"):
        # Find patient by username
        patient = next((p for p in manager.patients if p.username == username), None)

        if not patient:
            st.error("Unexpected Error!")
            return

        st.subheader("Patient Profile")

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
                # Get and clean birthday
                bday = getattr(patient, "bday", None)

                # Handle missing or string birthday safely
                if not bday:
                    bday = datetime.date(2000, 1, 1)
                elif isinstance(bday, str):
                    try:
                        # ISO format (YYYY-MM-DD)
                        bday = datetime.date.fromisoformat(bday)
                    except ValueError:
                        try:
                            # Fallback for DD/MM/YYYY
                            bday = datetime.datetime.strptime(bday, "%d/%m/%Y").date()
                        except ValueError:
                            bday = datetime.date(2000, 1, 1)

                # Streamlit date input (safe to use)
                new_bday = st.date_input("Birthday", value=bday)

                # Calculate age based on selected date
                today = datetime.date.today()
                age = today.year - new_bday.year - ((today.month, today.day) < (new_bday.month, new_bday.day))
                # Display in Streamlit

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
                result = User.update_patient_detail(manager, username, new_password, new_name, new_gender, new_address, new_email, new_contact_num, new_remark)
                with st.spinner("Saving changes..."):
                    time.sleep(1)
                if result:
                    manager.save()
                    st.toast("Successfully Updated!")
                    st.rerun()