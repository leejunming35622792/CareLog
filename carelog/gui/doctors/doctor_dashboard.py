import datetime
import streamlit as st

# details manager functions
from helper_manager.profile_manager import (
    view_doctor_details
)

# Appointment manager
from helper_manager.appointment_manager import AppointmentManager

# DASHBOARD
def dashboard(manager, username):
    """Main dashboard showing overview and quick stats"""
    # Page design
    st.markdown("<h1 style='text-align: center;'>Welcome to CareLog!</h1>", unsafe_allow_html=True)
    st.balloons()
    st.image("img/dashboard.png")
    st.divider()
    st.header("Dashboard Overview")

    # --- Doctor Details ---
    success, message, profile = view_doctor_details(username)

    if profile:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Doctor ID", profile.get("staff_id", "N/A"))
        with col2:
            st.metric("Department", profile.get("department", "Not Set"))
        with col3:
            st.metric("Speciality", profile.get("speciality", "Not Set"))

        st.divider()

        # --- Appointment ---
        st.header("Today's Appointments")
        appt_manager = AppointmentManager(manager)
        success, msg, appointments = appt_manager.view_upcoming_appointments(username)

        if success and appointments:
            today = datetime.datetime.now().strftime("%Y-%m-%d")  # ✅ fixed
            today_appts = [a for a in appointments if a.get("date") == today]
            if today_appts:
                for appt in today_appts[:3]:
                    st.info(
                        f"🕐 {appt.get('time','--:--')} - {appt.get('patient_name','Unknown')} ({appt.get('status','—')})"
                    )
            else:
                st.success("No appointments scheduled for today")
        else:
            st.info("No upcoming appointments")
    else:
        st.error(message)