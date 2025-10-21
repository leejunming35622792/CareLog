import streamlit as st
from helper_manager.remark_manager import (add_patient_remark_nurse, view_patient_remarks_nurse, update_patient_remark_nurse, delete_patient_remark_nurse)

def remarks_page(manager, username):
    """Remarks Management Page"""
    st.header("Patient Remarks Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Add Remark",
        "View Remarks",
        "Update Remark", 
        "Delete Remark"
    ])
    
    #Add Remark
    with tab1:
        with st.form("add_remark_form"):
            st.markdown("### Add New Remark")
            patient_id_remark = st.text_input("Patient ID", key="add_rem_pid")
            remark_type = st.selectbox(
                "Remark Type", 
                ["mood", "pain_level", "general", "observation", "vital_signs", "medication_response"],
                key="remark_type"
            )
            remark_content = st.text_area("Remark Content", key="remark_content")
            
            submitted = st.form_submit_button("➕ Add Remark", use_container_width=True)
            if submitted:
                if patient_id_remark and remark_content:
                    success, msg, rid = add_patient_remark_nurse(
                        patient_id_remark, username, remark_type, remark_content
                    )
                    if success:
                        st.success(f"✅ {msg} (Remark ID: {rid})")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please fill in all fields")
    
    #View Remarks
    with tab2:
        st.subheader("👁️ View Patient Remarks")
        patient_id_remarks = st.text_input("Enter Patient ID", key="view_remarks_pid")
        if st.button("🔍 View Remarks", key="view_remarks_btn"):
            if patient_id_remarks:
                success, msg, remarks = view_patient_remarks_nurse(patient_id_remarks)
                if success:
                    st.success(msg)
                    for remark in remarks:
                        with st.expander(f"Remark {remark['remark_id']} - {remark['type']} - {remark['timestamp']}"):
                            st.write(f"**Doctor ID:** {remark['doctor_id']}")
                            st.write(f"**Content:** {remark['content']}")
                            st.write(f"**Last Modified:** {remark['last_modified']}")
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a Patient ID")
    
    #Update Remark
    with tab3:
        with st.form("update_remark_form"):
            st.markdown("### Update Existing Remark")
            remark_id_upd = st.number_input("Remark ID", min_value=1, step=1, key="upd_rem_id")
            new_content = st.text_area("New Content", key="upd_rem_content")
            
            submitted = st.form_submit_button("💾 Update Remark", use_container_width=True)
            if submitted:
                if remark_id_upd and new_content:
                    success, msg, rid = update_patient_remark_nurse(remark_id_upd, new_content)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please enter Remark ID and new content")
    
    #Delete Remark
    with tab4:
        st.markdown("### Delete Remark")
        st.warning("This will deactivate the remark")
        
        remark_id_del = st.number_input("Remark ID to Delete", min_value=1, step=1, key="del_rem_id")
        confirm_delete_rem = st.checkbox("I confirm I want to delete this remark", key="confirm_del_rem")
        
        if st.button("🗑️ Delete Remark", type="primary", use_container_width=True):
            if remark_id_del and confirm_delete_rem:
                success, msg, rid = delete_patient_remark_nurse(remark_id_del)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter a Remark ID and confirm deletion")