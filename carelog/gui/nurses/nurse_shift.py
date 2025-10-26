import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# start of the shift page for nurses 
def shift_page():
    manager = st.session_state.manager
    username = st.session_state.username
    nurse = next((d for d in manager.nurses if d.username == username), None)

    st.title("Shift Schedule 📆")
    # get all shifts for the nurse
    if not nurse:
        st.warning("No nurse found for this username.")
        return

    # load raw data
    data = manager._load_data()
    all_staff_shifts = data.get("shifts", [])
    all_shifts = [shift for shift in all_staff_shifts if shift.get("staff_id") == nurse.n_id]

    if not all_shifts:
        st.info("No shifts assigned yet.")
        return

    for index, shift in enumerate(all_shifts):
        with st.form(f'shift_{index}'):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Shift ID", shift.get("shift_id"))
            with col2:
                st.metric("Day", shift.get("day"))
            with col3:
                st.metric("Start Time", shift.get("start_time"))
                st.metric("End Time", shift.get("end_time"))
            button = st.form_submit_button(label="View Only", disabled=True)


