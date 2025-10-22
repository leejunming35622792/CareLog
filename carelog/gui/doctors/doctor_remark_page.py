import streamlit as st
from datetime import datetime, timedelta

# Remark manager backend functions
from helper_manager.remark_manager import (
    view_patient_remarks,
    add_patient_remark,
    get_recent_patient_remarks,
    edit_patient_remark,
    delete_patient_remark,
)


def remarks_page(manager, username):
    """Doctor-facing page to view/add/edit patient remarks."""
    st.header("Patient Remarks")

    tab1, tab2, tab3, tab4 = st.tabs([
        "View",
        "Add",
        "Edit",
        "Delete",
    ])

    # Tab 1: View remarks
    with tab1:
        st.subheader("View Patient Remarks")
        patient_ids = [getattr(p, "p_id", "") for p in getattr(manager, "patients", [])]
        pid = st.selectbox("Patient ID", options=([""] + patient_ids))
        rtype = st.selectbox(
            "Filter by Type (optional)",
            ["All", "mood", "pain_level", "dietary", "general", "observation"],
        )
        limit = st.number_input("Limit (0 = show all)", min_value=0, max_value=200, value=0)
        if st.button("View Remarks"):
            if not pid:
                st.error("Please select a patient ID")
            else:
                remark_type = None if rtype == "All" else rtype
                lim = None if limit == 0 else int(limit)
                ok, msg, items = view_patient_remarks(pid, remark_type=remark_type, limit=lim)
                if ok and items:
                    st.success(msg)
                    for it in items:
                        label = f"{it.get('remark_type','').upper()} — {it.get('timestamp','')}"
                        with st.expander(label):
                            st.write(f"Doctor: {it.get('doctor_name','Unknown')}")
                            st.write(it.get("content", ""))
                            st.caption(f"Last Modified: {it.get('last_modified','')}")
                else:
                    st.info(msg or "No remarks found")

        st.divider()
        st.subheader("View Recent (by days)")
        pid_recent = st.selectbox("Patient ID (recent)", options=([""] + patient_ids), key="pid_recent")
        days = st.number_input("Days", min_value=1, max_value=365, value=7)
        if st.button("View Recent Remarks"):
            if not pid_recent:
                st.error("Please select a patient ID")
            else:
                ok, msg, items = get_recent_patient_remarks(pid_recent, int(days))
                if ok and items:
                    st.success(msg)
                    for it in items:
                        with st.expander(f"{it.get('remark_type','').upper()} — {it.get('timestamp','')}"):
                            st.write(f"Doctor: {it.get('doctor_name','Unknown')}")
                            st.write(it.get("content", ""))
                else:
                    st.info(msg or f"No remarks in last {days} days")

    # Tab 2: Add remark
    with tab2:
        st.subheader("Add Remark")
        pid_add = st.selectbox("Patient ID", options=([""] + patient_ids), key="pid_add")
        rtype_add = st.selectbox("Remark Type", ["mood", "pain_level", "dietary", "general", "observation"])
        content = st.text_area("Content", height=120)
        if st.button("Add Remark"):
            if not pid_add or not content.strip():
                st.error("Please select a patient and enter content")
            else:
                ok, msg, rid = add_patient_remark(pid_add, username, rtype_add, content.strip())
                if ok:
                    st.success(f"{msg} (ID: {rid})")
                else:
                    st.error(msg)

    # Tab 3: Edit remark
    with tab3:
        st.subheader("Edit Remark (only your own)")
        rid = st.text_input("Remark ID (e.g., RM0002)")
        new_content = st.text_area("New Content", height=120)
        if st.button("Save Edit"):
            if not rid or not new_content.strip():
                st.error("Please enter a remark ID and new content")
            else:
                ok, msg = edit_patient_remark(rid, username, new_content.strip())
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab4:
        st.markdown("### Delete Remark")
        st.warning("This will deactivate the remark")
        
        remark_id_del = st.number_input("Remark ID to Delete", min_value=1, step=1, key="del_rem_id")
        confirm_delete_rem = st.checkbox("I confirm I want to delete this remark", key="confirm_del_rem")
        
        if st.button("🗑️ Delete Remark", type="primary", use_container_width=True):
            if remark_id_del and confirm_delete_rem:
                success, msg, rid = delete_patient_remark(remark_id_del, username)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter a Remark ID and confirm deletion")
        