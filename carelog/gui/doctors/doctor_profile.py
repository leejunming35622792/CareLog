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

    # Variables
    success, message, profile = view_doctor_details(username)
    current_doctor = next((d for d in manager.doctors if d.username == username), None)
    
    if not current_doctor:
        st.warning("⚠️ Unexpected error - Please try again")
        st.stop()

    if not profile:
        st.error(message)
        return
 
    # Page design
    if profile.get("gender") == "Male":
        disp = "Your Profile 👨‍⚕️"
    elif profile.get("gender") == "Female":
        disp = "Your Profile 👩‍⚕️"
    else:
        disp = "Your Profile"
    st.markdown(f"<h1 style='text-align: center; font-size: 200%'>{disp}</h1>", unsafe_allow_html=True)
    st.divider()

    st.header("Current Profile Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=current_doctor.name or "", disabled=True)
        st.text_input("Email", value=current_doctor.email or "", disabled=True)
        st.text_input("Gender", value=current_doctor.gender, disabled=True)
        st.text_input("Date of Birth", value=current_doctor.bday, disabled=True)
    with col2:
        st.text_input("Contact Number", value=current_doctor.contact_num or "", disabled=True)
        st.text_area("Address", value=current_doctor.address or "", disabled=True)
        st.text_input("Department", value=current_doctor.department or "", disabled=True)
        st.text_input("Speciality", value=current_doctor.speciality or "", disabled=True)

    st.divider()
    st.header("Update Profile")

    with st.form("update_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("New Name")
            new_email = st.text_input("New Email")
            new_gender = st.selectbox("New Gender", ["Male", "Female", "Other"])
            new_password = st.text_input("New Password", type="password")
        with c2:
            new_contact = st.text_input("New Contact Number")
            new_address = st.text_area("New Address")
            new_department = st.text_input("New Department")
            new_speciality = st.text_input("New Speciality")

        submitted = st.form_submit_button("Update Profile")

        if submitted:
            ok = update_doctor_details(
                manager=manager,
                username=username,
                new_password=new_password or None,
                new_name=new_name.title() or None,
                new_gender=new_gender or None,
                new_address=new_address or None,
                new_email=new_email or None,
                new_contact_num=new_contact or None,
                new_department=new_department or None,
                new_speciality=new_speciality or None,
            )
            if ok:
                st.session_state.success_msg = "✅ Profile updated successfully!"
                manager.save()
                st.rerun()
            else:
                st.error("Failed to update profile")

    if "success_msg" in st.session_state and st.session_state.success_msg != "":
        st.success(st.session_state.success_msg)
        st.session_state.success_msg = ""