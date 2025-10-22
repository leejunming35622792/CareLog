import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Remark manager
from helper_manager.remark_manager import (
    view_patient_remarks,
    add_patient_remark,
    get_recent_patient_remarks,
    edit_patient_remark,
)

def remarks_page(manager,username):
    "Manage remarks related to patients."
    st.title("Patient Remarks Management")
    tab1, tab2, tab3, tab4 = st.tabs(["View Patient Remarks", "Add Remark", "Edit Remark", "Delete Remarks"])
    with tab1:
        st.title("View Patient Remarks")
        view_patient_id=st.dropdown("Select Patient ID", options=manager.get_all_patient_ids())
        