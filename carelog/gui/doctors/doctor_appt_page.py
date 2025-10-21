import streamlit as st

# Appointment manager
from helper_manager.appointment_manager import AppointmentManager

# APPOINTMENTS
def appointments_page(manager, username):
    """View and manage appointments"""
    st.header("Appointments")
    appt_manager = AppointmentManager(manager)
    success, message, appointments = appt_manager.view_all_appointments(username)

    if not success:
        st.error(message)
        return

    if not appointments:
        st.info("No upcoming appointments scheduled")
        return

    st.success(message)
    c1, c2 = st.columns(2)
    with c1:
        enable_date_filter = st.checkbox("Filter by Date (optional)")
        filter_date = st.date_input("Pick a Date") if enable_date_filter else None
    with c2:
        filter_status = st.selectbox(
            "Filter by Status", ["All", "Pending", "Confirmed", "Completed", "Cancelled"]
        )

    filtered_appts = appointments
    if filter_date:
        target = filter_date.strftime("%Y-%m-%d")
        filtered_appts = [a for a in filtered_appts if a.get("date") == target]
    if filter_status != "All":
        filtered_appts = [a for a in filtered_appts if a.get("status") == filter_status]

    st.divider()
    if filtered_appts:
        for appt in filtered_appts:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**📅 {appt.get('date','—')}**")
                with col2:
                    st.write(f"**🕐 {appt.get('time','--:--')}**")
                with col3:
                    st.write(f"**👤 {appt.get('patient_name','Unknown')}** (ID: {appt.get('patient_id','—')})")
                with col4:
                    status_color = {
                        "Pending": "🟡", "Confirmed": "🟢", "Completed": "🔵", "Cancelled": "🔴",
                    }
                    st.write(f"{status_color.get(appt.get('status'), '⚪')} {appt.get('status','—')}")
                if appt.get("remark"):
                    st.caption(f"Note: {appt['remark']}")
                st.divider()
    else:
        st.info("No appointments match the selected filters")