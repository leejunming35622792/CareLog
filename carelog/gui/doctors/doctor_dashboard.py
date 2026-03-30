import datetime
import streamlit as st
from helper_manager.profile_manager import (view_doctor_details)
from helper_manager.profile_manager import (view_patient_details_by_nurse, search_patient_by_name)
from helper_manager.appointment_manager import AppointmentManager

# DASHBOARD
def dashboard(manager, username):
    # main variables
    manager = st.session_state.manager
    username = st.session_state.username
    current_doctor = next((d for d in manager.doctors if d.username == st.session_state.username))

    # page design 
    st.markdown("<h1 style='text-align: center;'>Welcome to CareLog!</h1>", unsafe_allow_html=True)
    st.image("img/dashboard.png")
    st.divider()
    st.header("Dashboard Overview 🎗️")

    # details of the doctor profile 
    success, message, profile = view_doctor_details(username)

    if profile:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Doctor ID", current_doctor.d_id)
        with col2:
            st.metric("Department", profile.get("department", "Not Set"))
        with col3:
            st.metric("Speciality", profile.get("speciality", "Not Set"))

        st.divider()

    #search for patient profile 
    st.header("Quick Search 🔍")
    st.write("")
    with st.expander("Filter Patients", expanded=True):
        search_type = st.radio("Search By:", ["Patient ID", "Name"], horizontal=True)

        if search_type == "Patient ID":
            query = st.text_input("Enter search value", value="P000X")
        else:
            query = st.text_input("Enter search value", placeholder="")

        if st.button("Search🔍", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a value to search ⚠️")
            else:
                if search_type == "Patient ID":
                    try:
                        patient_id = int(query) if query.isdigit() else query
                        success, msg, info = view_patient_details_by_nurse(patient_id)
                    except ValueError:
                        st.error("Invalid Patient ID format")
                        return
                else:
                    success, msg, info = search_patient_by_name("doctor", username, query)

                if success:
                    st.success(msg)
                    st.divider()
                    if isinstance(info, list):
                        for patient in info:
                            with st.container():
                                st.markdown(f"<h1 style='font-size:150%'>🧍{patient['name']} (ID: {patient['patient_id']})</h1>", unsafe_allow_html=True)
                                st.markdown(f"<span style='font-size:150%'>💌 </span><span style='font-size:100%'>{patient['email']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span style='font-size:150%'>📞 </span><span style='font-size:100%'>{patient['contact']}</span>", unsafe_allow_html=True)
                                st.markdown("_____")
                    else:
                        st.json(info)
                else:
                    st.error(msg)
    
    st.divider()

    #view today's upcoming appointments
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    st.header(f"Today's Appointments ({today}) 📄")
    st.write("")

    appt_manager = AppointmentManager(manager)
    success, msg, appt_list = appt_manager.list(manager, "doctor", username, scope="own", upcoming_only=False, date=today, status=None, doctor_id=current_doctor.d_id, appt_id=None)
    #display appointments
    if success and appt_list:
        for appt in appt_list:
            with st.expander(f"Appointment {appt["appt_id"]}"):
                col1, col2, col3 = st.columns([1,2,2])
                with col1:
                    st.metric("Appointment", appt["appt_id"])
                    st.metric("Patient", appt["patient_name"], delta=appt["patient_id"], delta_color="off")
                with col2:
                    risk_color = {
                        "Booked": "green",
                        "Pending": "blue",
                        "Scheduled": "blue",
                        "Rescheduled": "orange",
                        "Cancelled": "red"
                    }

                    status = appt['status'].capitalize()
                    color = risk_color.get(status, "black")
                    #display date and time
                    st.markdown(
                        f"""
                        <div style="
                        display:flex; 
                        justify-content: space-between; 
                        align-items:center; 
                        padding:15px 30px; 
                        font-size:200%">
                            <div style="font-weight:bold;">Time:</div>
                            <div>{appt['time']}</div>

                        </div>
                        <div style="display:flex; 
                        justify-content: space-between; 
                        align-items:center; 
                        padding:15px 30px; 
                        font-size:200%">
                            <div style="font-weight:bold;">Status:</div>
                            <div style="color:{color}; font-weight:bold;"> {status}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col3:
                    st.text_area("Remark", appt["remark"], key=f"remark_disp_{appt["appt_id"]}", disabled=True, height='stretch')
    else:
        st.info("No upcoming appointments")

    st.divider()

   #view appointment of this months
    today = datetime.datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    current_month = today.month
    current_year = today.year
    st.header(f"Appointments for {today.strftime('%B %Y')} 📅")
    st.write("")
    st.write("")

    #retrieve appointments for the doctor user
    appt_manager = AppointmentManager(manager)
    success, msg, appt_list = appt_manager.list(manager, "doctor", username, scope="own", upcoming_only=False, status=None, doctor_id=current_doctor.d_id, appt_id=None)

    if success and appt_list:
        month_appts = [
            appt for appt in appt_list 
            if datetime.datetime.strptime(appt["date"], "%Y-%m-%d").month == current_month
            and datetime.datetime.strptime(appt["date"], "%Y-%m-%d").year == current_year
        ]
        for appt in month_appts:
            with st.expander(f"Appointment {appt["appt_id"]}"):
                col1, col2, col3 = st.columns([1,2,2])
                with col1:
                    st.metric("Appointment", appt["appt_id"])
                    st.metric("Patient", appt["patient_name"], delta=appt["patient_id"], delta_color="off")
                with col2:
                    risk_color = {
                        "Booked": "green",
                        "Scheduled": "blue",
                        "Pending": "blue",
                        "Rescheduled": "orange",
                        "Cancelled": "red"
                    }

                    status = appt['status'].title()
                    color = risk_color.get(status, "red")
                    #display date and time
                    st.markdown(
                        f"""
                        <div style="
                        display:flex; 
                        justify-content: space-between; 
                        align-items:center; 
                        padding:15px 30px; 
                        font-size:200%">
                            <div style="font-weight:bold;">Date:</div>
                            <div>{appt['date']}</div>
                        </div>

                        <div style="
                        display:flex; 
                        justify-content: space-between; 
                        align-items:center; 
                        padding:15px 30px; 
                        font-size:200%">
                            <div style="font-weight:bold;">Time:</div>
                            <div>{appt['time']}</div>
                        </div>

                        <div style="display:flex; 
                        justify-content: space-between; 
                        align-items:center; 
                        padding:15px 30px; 
                        font-size:200%">
                            <div style="font-weight:bold;">Status:</div>
                            <div style="color:{color}; font-weight:bold;"> {status}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col3:
                    st.text_area("Remark",appt["remark"], disabled=True, height='stretch', key=f"remark_{appt['appt_id']}")
    else:
        st.info("No upcoming appointments")