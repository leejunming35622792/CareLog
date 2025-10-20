import streamlit as st
import pandas as pd
from helper_manager.record_manager import search_record

def record(manager):
    # Variable
    username = st.session_state.username

    # Page design
    st.markdown("<h1 style='text-align: center; font-size: 300%'>--- CareLog ---</h1>", unsafe_allow_html=True)

    # --- Find patient ---
    patient = next((p for p in manager.patients if p.username == username), None)

    # --- Get all record IDs for patient ---
    p_record_id = [r.pr_record_id for r in manager.records if r.pr_record_id in patient.p_record]
    if not p_record_id:
        st.warning("No records found!")
        return

    st.subheader("Patient Records")

    # --- Record selection ---
    record_id = st.selectbox("Select Record ID", p_record_id)

    # --- Display selected record ---
    current_record = search_record(patient.p_id, record_id)

    # Convert object to readable table
    record_df = pd.Series(current_record).to_frame("Details")
    st.dataframe(record_df)
