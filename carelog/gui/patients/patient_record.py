import streamlit as st
from helper_manager.record_manager import (
    search_record,
    print_record
)

def record(manager):
    # Variable
    username = st.session_state.username
    patient = next((p for p in manager.patients if p.username == username), None)
    if patient is None:
        st.error("Patient not found!")
        return

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    with st.form("view-record-form"):
        st.markdown(f"<h1 style='text-align: center; font-size: 200%'>Records 📃</h1>", unsafe_allow_html=True)

        # Get all record IDs for patient 
        p_record_id = [r.pr_record_id for r in manager.records if r.pr_record_id in patient.p_record]

        col1, col2, col3= st.columns([3,1,3])
        with col1:
            # Choose record 
            record_id = st.selectbox("Select Record ID", p_record_id)
            
        with col3:
            st.markdown("")
            if p_record_id:
                show = False
            else:
                show = True
            view_button = st.form_submit_button("View Record", disabled = show, use_container_width=True)
            download_button = st.form_submit_button("Download Record", disabled = show, use_container_width=True)

        st.divider()
        if not p_record_id:
            st.warning("No records found!")

        # Get current record first
        current_record = search_record(patient.p_id, record_id)

        if view_button:
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
            success, msg, file_dir = print_record(manager, username, current_record)
            st.session_state.success_msg = msg
            st.rerun()

        with st.expander("ℹ️ Learn more about Confidence Score and Prediction Result"):
            st.write("""
            - **Prediction Result** indicates the system’s analysis of your medical record, estimating your **current health risk level** (e.g., *Low*, *Moderate*, or *High*).  
            This result is derived from patterns in your clinical data such as symptoms, test results, and treatment history.
            
            - **Confidence Score** reflects how certain the AI model is about its prediction.  
            A higher score (close to 100%) means the system found strong evidence or consistent data patterns supporting that risk level,  
            while a lower score suggests uncertainty — often due to limited or inconsistent data in your record.
            """)
