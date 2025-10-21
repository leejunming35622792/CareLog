import streamlit as st
import pandas as pd
from helper_manager.record_manager import search_record
from helper_manager.record_manager import print_record

def record(manager):
    # Variable
    username = st.session_state.username
    patient = next((p for p in manager.patients if p.username == username), None)

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    with st.form("view-record-form"):
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Records 📃</h1>", unsafe_allow_html=True)
        col1, col2, col3= st.columns([3,1,3])
        with col1:
            # --- Get all record IDs for patient ---
            p_record_id = [r.pr_record_id for r in manager.records if r.pr_record_id in patient.p_record]
            if not p_record_id:
                st.warning("No records found!")
                return
            
            # --- Record selection ---
            record_id = st.selectbox("Select Record ID", p_record_id)
            
        with col3:
            st.markdown("")
            view_button = st.form_submit_button("View Record", use_container_width=True)
            download_button = st.form_submit_button("Download Record", use_container_width=True)

        st.divider()

        if view_button:
            # --- Display selected record ---
            current_record = search_record(patient.p_id, record_id)

            # --- Display as a dashboard ---
            st.markdown(f"### Record: {current_record['Record ID']} (Date: {current_record['Date'][:10]})")

            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Billings (RM)", current_record["Billings"])
            col2.metric("Confidence Score", f"{current_record['Confidence Score']*100:.1f}%")

            # Conditions and Medications as badges
            st.markdown(f"**Condition:** <span style='background-color: #f0ad4e; padding: 4px; border-radius: 5px; margin: 10px'>{current_record['Conditions']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Medications:** <span style='background-color: #5bc0de; padding: 4px; border-radius: 5px; margin: 10px'>{current_record['Medications']}</span>", unsafe_allow_html=True)

            # Risk color coding
            risk_color = {
                "Low risk": "green",
                "Moderate risk": "orange",
                "High risk": "red"
            }
            color = risk_color.get(current_record["Prediction Result"], "black")
            st.markdown(f"**Prediction Result:** <span style='color:{color};; font-size:150%'><b>     {current_record['Prediction Result']}</b></span>", unsafe_allow_html=True)

            # Optional details in expander
            with st.expander("More Details"):
                st.write("Remark:", current_record["Remark"])

        if download_button:
            record_searched = search_record(patient.p_id, record_id)
            # print_record()

        
