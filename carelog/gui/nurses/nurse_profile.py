import streamlit as st
from app.user import User

def profile_page(manager, username):
    # Page design
    st.header("👩‍⚕️ My Profile")

    # Variables
    nurse = next((n for n in manager.nurses if n.username == username), None)

    with st.form("update_nurse_profile"):
        with st.container():
            st.markdown("### 👤 Personal Details")
            st.write(" ")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.text_input("Name", value=nurse.name)
                st.text_input("Gender", value=nurse.gender)
                st.text_input("Date Joined", value=nurse.date_joined)
            with col2:
                st.text_input("Email", value=nurse.email)
                st.text_input("Contact", value=nurse.contact_num)
                st.text_input("Address", value=nurse.address)

        st.markdown("### 🏥 Professional Details")
        col3, col4 = st.columns(2)
        with col3:
            st.text_input("Department", value=nurse.department)
        with col4:
            st.text_input("Speciality", value=nurse.speciality)

        st.markdown("")
        submitted = st.form_submit_button("💾 Save Changes")

        if submitted:
            pass

