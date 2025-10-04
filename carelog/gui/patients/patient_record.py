import streamlit as st
import pandas as pd

def record(manager):
    # Variables
    username = st.session_state.username

    # Page design
    st.title("CareLog - We Know You")

    with st.container():
        # Variables
        patient = next((p for p in manager.patients if p.username == username), None)
        p_record_id = [record.pr_record_id for record in manager.records if record.p_id in patient.p_record]

        if not patient:
            st.error("Unexpected Error!")
            return
        if not p_record_id:
            st.warning("No records found!")
            return
        
        st.subheader("Patient Records")
        
        # Input box
        choose_record = st.selectbox("Select Record ID", p_record_id)
        current_record = manager.search_record(patient.p_id, choose_record)

        # Display using dataframe
        if current_record:
            record_df = pd.Series(current_record).to_frame("")
            st.dataframe(record_df)
        else:
            st.warning("No records found!")

        

