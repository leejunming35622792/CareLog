import streamlit as st
import datetime
from helper_manager.profile_manager import find_age
from gui.patients.chat_box import chat_box

def dashboard(manager, username):
    # get current patient based on the username
    current_patient = next((p for p in manager.patients if p.username == username))
    
    # page design 
    st.markdown("<h1 style='text-align: center;'>Welcome to CareLog!</h1>", unsafe_allow_html=True)
    st.image("img/dashboard.png")
    st.divider()

    # dahsboard overview
    st.header("Dashboard Overview 🎗️")
    st.write("")
    m1, m2, m3 = st.columns(3)

    with m1:
        # name
        p_name = current_patient.name
        st.metric("Name", p_name)
    with m2:
        # age
        p_age = find_age(current_patient.bday)
        st.metric("Age", p_age)
    with m3:
        # get all Last record 
        patient_records = [record for record in manager.records if record.p_id == current_patient.p_id]
        # if got records
        if patient_records:
            # find last record date
            latest_record = max(patient_records, key=lambda r: r.pr_timestamp)
            latest_record_str = datetime.datetime.fromisoformat(latest_record.pr_timestamp).strftime("%Y-%m-%d")
            # find days past
            today = datetime.datetime.now()
            last_record_dt = datetime.datetime.fromisoformat(latest_record.pr_timestamp)
            days_difference = (today - last_record_dt).days
            st.metric("Last Record", latest_record_str, delta=f"{days_difference} days")
        else:
            st.info("Book a medical check-up with us right now! 😊") 

    st.divider()

    #chatbox
    st.header("CareBot 💬")
    st.write("")
    chat_box()
