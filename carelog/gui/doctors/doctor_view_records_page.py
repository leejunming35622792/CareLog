import streamlit as st

# details manager functions
from helper_manager.profile_manager import view_patient_details_by_doctor

# Remark manager
from helper_manager.remark_manager import (
    view_patient_remarks,
    add_patient_remark,
    get_recent_patient_remarks,
    edit_patient_remark,
)

def patient_records_page(manager, username):
    """View patient details and manage remarks"""
    st.header("Patient Records")

    tab1, tab2, tab3 = st.tabs(["View Patient Details", "Add Remark", "View Remarks"])

    # Tab 1: View Patient
    with tab1:
        st.markdown("#### Search by ID")
        patient_id = st.text_input("Enter Patient ID", key="patient_search_records")
        if st.button("Search Patient", key="search_btn"):
            success, message, info = view_patient_details_by_doctor(patient_id)
            if success and info:
                st.success(message)
                # Top-level metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Patient ID", info.get("patient_id", "N/A"))
                    st.metric("Name", info.get("name", "N/A"))
                    st.metric("Gender", info.get("gender", "N/A"))
                    st.metric("Date of Birth", info.get("date_of_birth", "N/A"))
                with col2:
                    # Normalize previous_conditions to a list of strings
                    raw_prev = info.get("previous_conditions", [])
                    prev_list = []
                    if isinstance(raw_prev, dict):
                        # dict of condition -> severity/notes
                        prev_list = [f"{k}: {v}" for k, v in raw_prev.items()]
                    elif isinstance(raw_prev, list):
                        prev_list = [str(x) for x in raw_prev]
                    elif isinstance(raw_prev, str):
                        prev_list = [raw_prev] if raw_prev.strip() else []

                    st.write("**Previous Conditions:**")
                    if prev_list:
                        for condition in prev_list:
                            st.write(f"• {condition}")
                    else:
                        st.info("No previous conditions recorded")

                    # Normalize medication_history to a list of strings
                    raw_med = info.get("medication_history", [])
                    med_list = []
                    if isinstance(raw_med, dict):
                        med_list = [f"{k}: {v}" for k, v in raw_med.items()]
                    elif isinstance(raw_med, list):
                        med_list = [str(x) for x in raw_med]
                    elif isinstance(raw_med, str):
                        med_list = [raw_med] if raw_med.strip() else []

                    st.write("**Medication History:**")
                    if med_list:
                        for med in med_list:
                            st.write(f"• {med}")
                    else:
                        st.info("No medication history recorded")
            else:
                st.error(message or "Patient not found.")

    # Tab 2: Add Remark
    with tab2:
        st.subheader("Add Patient Remark")
        with st.form("add_remark_form"):
            patient_id_remark = st.text_input("Enter Patient ID", key="patient_search_remark")
            remark_type = st.selectbox(
                "Remark Type", ["mood", "pain_level", "dietary", "general", "observation"]
            )
            remark_content = st.text_area("Remark Content", height=150)
            submitted = st.form_submit_button("Add Remark")

            if submitted:
                if not remark_content.strip():
                    st.error("Please enter remark content")
                else:
                    success, message, remark_id = add_patient_remark(
                        patient_id=patient_id_remark,
                        doctor_username=username,
                        remark_type=remark_type,
                        remark_content=remark_content,
                    )
                    if success:
                        st.success(f"✅ {message} (Remark ID: {remark_id})")
                    else:
                        st.error(message)

    # Tab 3: View/Edit Remarks
    with tab3:
        st.subheader("View Patient Remarks")
        view_patient_id = st.text_input("Enter Patient ID", key="patient_search_remark_view")
        filter_type = st.selectbox(
            "Filter by Type (optional)",
            ["All", "mood", "pain_level", "dietary", "general", "observation"],
        )
        days_filter = st.number_input("Recent Days", min_value=1, max_value=365, value=7)

        if st.button("View All Remarks"):
            remark_type_filter = None if filter_type == "All" else filter_type
            success, message, remarks = view_patient_remarks(
                patient_id=view_patient_id, remark_type=remark_type_filter
            )
            if success and remarks:
                # Store remarks in session state for dropdown access
                if 'current_remarks' not in st.session_state:
                    st.session_state.current_remarks = []
                st.session_state.current_remarks = remarks
                
                for remark in remarks:
                    with st.expander(
                        f"{remark['remark_type'].upper()} - {remark['timestamp']} by {remark['doctor_name']}"
                    ):
                        st.write(remark["content"])
                        st.caption(f"Last Modified: {remark['last_modified']}")
                
                # Edit section with dropdown
                st.markdown("---")
                st.subheader("Edit Remark")
                with st.form("edit_remark_form"):
                    
                    remark_options = [
                        f"{r['remark_id']} - {r['remark_type'].upper()} ({r['timestamp'][:10]})"
                        for r in remarks
                    ]
                    selected_remark_display = st.selectbox(
                        "Select Remark to Edit",
                        options=remark_options,
                        help="Choose which remark you want to edit"
                    )
                    
                    if selected_remark_display:
                        # Extract remark_id from the selected option
                        selected_remark_id = selected_remark_display.split(' - ')[0]
                        selected_remark = next(
                            (r for r in remarks if r['remark_id'] == selected_remark_id), 
                            None
                        )
                        
                        if selected_remark:
                            st.info(f"**Current Content:** {selected_remark['content']}")
                            new_content = st.text_area(
                                "Edit Content", 
                                value=selected_remark['content'],
                                height=150
                            )
                            
                            if st.form_submit_button("💾 Save Edit"):
                                if new_content.strip():
                                    ok, msg = edit_patient_remark(
                                        remark_id=selected_remark_id,
                                        doctor_username=username,
                                        new_content=new_content,
                                    )
                                    if ok:
                                        st.success(f"✅ {msg}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                                else:
                                    st.error("Please enter remark content")
            else:
                st.info("No remarks found.")

        if st.button("View Recent Remarks"):
            success, message, remarks = get_recent_patient_remarks(
                patient_id=view_patient_id, days=days_filter
            )
            if success and remarks:
                for remark in remarks:
                    with st.expander(
                        f"{remark['remark_type'].upper()} - {remark['timestamp']}"
                    ):
                        st.write(f"**Doctor:** {remark['doctor_name']}")
                        st.write(remark["content"])
            else:
                st.info(f"No remarks found in the last {days_filter} days")

