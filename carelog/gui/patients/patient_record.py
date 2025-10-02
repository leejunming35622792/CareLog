import streamlit as st

def record(manager, username):
    with st.form("record-form"):
        patient = next((p for p in manager.patients if p.username == username), None)

        if not patient:
            st.error("Unexpected Error!")
            return
        
        st.subheader("Patient Records")