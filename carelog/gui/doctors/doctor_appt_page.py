import streamlit as st

# Appointment manager
from helper_manager.appointment_manager import AppointmentManager

#appointments page for doctor 
def appointments_page(manager, username):
    """View and manage appointments"""
    # variables from manager
    appt_manager = AppointmentManager(manager)
    result = appt_manager.view_all_appointments(manager, username)

    # page design
    st.title("Appointment Management 📅")
    tab1, tab2 = st.tabs(["View Appointments", "Update Appointments"])
    #view appointments tab section
    with tab1:
        st.header("View Appointments")   
        if len(result) == 3:
            success, message, appointments = result
        else:
            success, message = result
            appointments = []

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
                        st.write(f"**{appt.get('date','—')}**")
                    with col2:
                        st.write(f"**{appt.get('time','--:--')}**")
                    with col3:
                        st.write(f"**{appt.get('patient_name','Unknown')}** (ID: {appt.get('patient_id','—')})")
                    with col4:
                        status_color = {
                            "Pending": "🟡", "Confirmed": "🟢", "Completed": "🔵", "Cancelled": "🔴", 
                        }
                        st.write(f"{status_color.get(appt.get('status'), '⚪')} {appt.get('status','—')}")
                    if appt.get("remark"):
                        st.caption(f"Note: {appt['remark']}")
                    
                    #quick action buttons 
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("Complete✅", key=f"complete_{appt['appt_id']}"):
                            success, message, _ = appt_manager.update_appointment_doctor(
                                manager,
                                username,
                                appt_id=appt['appt_id'],
                                date=None,
                                time=None,
                                status="completed",
                                remark=None
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    with col2:
                        if st.button("Cancel❌", key=f"cancel_{appt['appt_id']}"): 
                            success, message, _ = appt_manager.update_appointment_doctor(
                                manager,
                                username,
                                appt_id=appt['appt_id'],
                                date=None,
                                time=None,
                                status="cancelled",
                                remark=None
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    st.divider()
        else:
            st.info("No appointments match the selected filters")

    with tab2:
        #update appointment tab section
        st.header("Update Appointment ")
        with st.form("update_appointment_form"):
            st.subheader("Update Appointment Details📝")
            appt_id_update = st.text_input("Appointment ID", placeholder="Enter appointment ID to update")
            
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("New Date (optional)", value=None, help="Leave empty to keep current date")
                new_status = st.selectbox("Update Status", 
                    ["", "scheduled", "completed", "cancelled", "no-show"],
                    help="Leave blank to keep current status")
            
            with col2:
                new_time = st.time_input("New Time (optional)", value=None, help="Leave empty to keep current time")
                new_remark = st.text_area("Update Remark (optional)", placeholder="Add or update appointment notes")
            
            submitted = st.form_submit_button(" Update Appointment", use_container_width=True)
            
            if submitted and appt_id_update:
                # Convert date and time to strings if provided
                date_str = new_date.strftime("%Y-%m-%d") if new_date else None
                time_str = new_time.strftime("%H:%M") if new_time else None
                status_str = new_status if new_status else None
                remark_str = new_remark if new_remark.strip() else None
                
                #calls the update appointment function from appointment manager
                success, message, updated_appt = appt_manager.update_appointment_doctor(
                    manager,
                    username,
                    appt_id=appt_id_update,
                    date=date_str,
                    time=time_str,
                    status=status_str,
                    remark=remark_str
                )
                
                if success:
                    st.success(f"{message}✅ ")
                    st.rerun()  # refreshes the page to update the data after changes
                else:
                    st.error(f"{message}❌")
            elif submitted:
                st.warning("Please enter an Appointment ID⚠️")        