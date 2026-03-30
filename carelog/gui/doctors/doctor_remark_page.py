import streamlit as st
import time
from datetime import datetime, timedelta

# remark manager backend functions
from helper_manager.remark_manager import (
    view_patient_remarks,
    add_patient_remark,
    get_recent_patient_remarks,
    edit_patient_remark,
    delete_patient_remark,
)

# start of the remark page for doctors
def remarks_page(manager, username):
    """Doctor-facing page to view/add/edit patient remarks."""
    curr_username = st.session_state.username
    curr_id = next((d.d_id for d in manager.doctors if d.username == curr_username), None)

    st.title("Patient Remarks 💭")

    tab1, tab2, tab3, tab4 = st.tabs([
        "View",
        "Add",
        "Edit",
        "Delete",
    ])

    # view patient's reamrks
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
                        label = f"{it.get('remark_type','').upper()} — {datetime.fromisoformat(it.get('timestamp',''))}"
                        with st.expander(label):
                            st.write(f"Doctor: {it.get('doctor_name','Unknown')}")
                            st.write("Remark: \n", it.get("content", ""))
                            st.caption(f"Last Modified: {datetime.fromisoformat(it.get('last_modified',''))}")
                else:
                    st.info(msg or "No remarks found")
        # view recent remarks by days
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
    
    # add remarks for patients
    with tab2:
        with st.form('add-remark', clear_on_submit=True):
            st.subheader("Add Remark")
            pid_add = st.selectbox("Patient ID", options=([""] + patient_ids), key="pid_add")
            rtype_add = st.selectbox("Remark Type", ["Mood", "Pain_level", "Dietary", "General", "Observation"])
            content = st.text_area("Content", height=120)
            submit_remark = st.form_submit_button("Add Remark")

            if submit_remark:
                if not pid_add or not content.strip():
                    st.error("Please select a patient and enter content")
                else:
                    ok, msg, rid = add_patient_remark(pid_add, username, rtype_add, content.strip())
                    if ok:
                        with st.spinner("Saving remark..."):
                            time.sleep(2)
                        st.success(f"{msg} (ID: {rid})")
                    else:
                        st.error(msg)

    # edit existing remarks 
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
    
    # delete existing remarks 
    with tab4:
        st.markdown("### Delete Remark")
        st.warning(f"⚠️ You are about to **cancel** the following remark and this action cannot be undone.")
        all_patient = {p.p_id:p.name for p in manager.patients}
        remark_disp = {f"{r.remark_id} - {all_patient[r.patient_id]}": r.remark_id for r in manager.remarks if r.doctor_id == curr_id}

        if not remark_disp:
            st.warning("⚠️ No remark found")
            st.stop()

        choose_remark_id = st.selectbox("Select Remark ID", remark_disp.keys())
        confirm_delete_rem = st.checkbox("I confirm I want to delete this remark", key="confirm_del_rem")
        
        if st.button("🗑️ Delete Remark", type="primary", use_container_width=True):
            remark_id_del = remark_disp[choose_remark_id]
            st.info(remark_id_del)

            if remark_id_del and confirm_delete_rem:
                success, msg, rid = delete_patient_remark(remark_id_del, username)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter a Remark ID and confirm deletion")
        