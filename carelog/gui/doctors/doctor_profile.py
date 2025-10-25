import streamlit as st

# details manager functions
from helper_manager.profile_manager import view_doctor_details

def update_doctor_details(manager, *, username,
                          new_password=None, new_name=None, new_gender=None,
                          new_address=None, new_email=None, new_contact_num=None,
                          new_department=None, new_speciality=None):
    """Update a doctor's fields by username and persist to JSON."""
    doc = next((d for d in manager.doctors if getattr(d, "username", None) == username), None)
    if not doc:
        return False
    if new_password:    doc.password    = new_password
    if new_name:        doc.name        = new_name
    if new_gender:      doc.gender      = new_gender
    if new_address:     doc.address     = new_address
    if new_email:       doc.email       = new_email
    if new_contact_num: doc.contact_num = new_contact_num
    if new_department:  doc.department  = new_department
    if new_speciality:  doc.speciality  = new_speciality
    if hasattr(manager, "save"): manager.save()
    return True

def profile_page(manager, username):
    """View and update doctor profile"""
    st.header("My Profile")

    success, message, profile = view_doctor_details(username)
    if not profile:
        st.error(message)
        return

    st.subheader("Current Profile Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=profile.get("name", ""), disabled=True)
        st.text_input("Email", value=profile.get("email", ""), disabled=True)
        st.text_input("Gender", value=profile.get("gender", ""), disabled=True)
        st.text_input("Date of Birth", value=profile.get("date_of_birth", ""), disabled=True)
    with col2:
        st.text_input("Contact Number", value=profile.get("contact_num", ""), disabled=True)
        st.text_area("Address", value=profile.get("address", ""), disabled=True)
        st.text_input("Department", value=profile.get("department", ""), disabled=True)
        st.text_input("Speciality", value=profile.get("speciality", ""), disabled=True)

    st.divider()
    st.subheader("Update Profile")

    with st.form("update_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("New Name (optional)")
            new_email = st.text_input("New Email (optional)")
            new_gender = st.selectbox("New Gender (optional)", ["", "Male", "Female", "Other"])
            new_password = st.text_input("New Password (optional)", type="password")
        with c2:
            new_contact = st.text_input("New Contact Number (optional)")
            new_address = st.text_area("New Address (optional)")
            new_department = st.text_input("New Department (optional)")
            new_speciality = st.text_input("New Speciality (optional)")

        submitted = st.form_submit_button("Update Profile")

        if submitted:
            ok = update_doctor_details(
                manager=manager,
                username=username,
                new_password=new_password or None,
                new_name=new_name or None,
                new_gender=new_gender or None,
                new_address=new_address or None,
                new_email=new_email or None,
                new_contact_num=new_contact or None,
                new_department=new_department or None,
                new_speciality=new_speciality or None,
            )
            if ok:
                st.session_state.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update profile")