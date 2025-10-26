import streamlit as st
import datetime
from helper_manager.appointment_manager import AppointmentManager

def appointment_page(manager):
    st.subheader("📅 Appointment")
    if not getattr(manager, "appointments", None):
        st.info("No appointments found.")

    actor_username = st.session_state.get("username", "")
    apptm = AppointmentManager(manager)

    top1, top2, top3 = st.columns([1, 1, 1])
    with top1:
        # Optional date filter (only applies if enabled)
        enable_date = st.checkbox("Filter by date", value=False, key="adm_appt_date_en")
        date_val = st.date_input("Date", datetime.date.today(), key="adm_appt_date") if enable_date else None
    with top2:
        # Single-status filter (AppointmentManager.list expects a single status or None)
        status_options = ["All", "scheduled", "booked", "rescheduled", "cancelled", "completed", "no-show", "pending"]
        status_sel = st.selectbox("Status", status_options, index=0, key="adm_appt_status")
    with top3:
        appt_id_filter = st.text_input("Appointment ID", key="adm_appt_id").strip()

    row2a, row2b, row2c, _ = st.columns([1, 1, 1, 1])
    with row2a:
        # Doctor filter
        doc_map = {"All doctors": None}
        doc_map.update({f"{d.name} ({d.d_id})": d.d_id for d in manager.doctors})
        doc_choice = st.selectbox("Doctor", list(doc_map.keys()), key="adm_appt_doc")
        doctor_id = doc_map[doc_choice]
    with row2b:
        # Patient filter
        pat_map = {"All patients": None}
        pat_map.update({f"{p.name} ({p.p_id})": p.p_id for p in manager.patients})
        pat_choice = st.selectbox("Patient", list(pat_map.keys()), key="adm_appt_pat")
        patient_id = pat_map[pat_choice]
    with row2c:
        upcoming_only = st.toggle("Upcoming only", value=False, key="adm_appt_upcoming")

    # Prepare filter args for list(...)
    date_str = date_val.isoformat() if date_val else None
    status_arg = None if status_sel == "All" else status_sel
    appt_id_arg = appt_id_filter if appt_id_filter else None

    # ---------- Fetch lists ----------
    # All (with filters)
    ok_all, msg_all, rows_all = apptm.list(manager, "admin", actor_username, scope="own", upcoming_only=False, date=date_str, status=status_arg, patient_id=patient_id, doctor_id=doctor_id, appt_id=appt_id_arg)

    # Upcoming (same filters + upcoming_only)
    ok_up, msg_up, rows_up = apptm.list(manager, "admin", actor_username, scope="own", upcoming_only=True if not date_str else False, date=date_str, status=status_arg, patient_id=patient_id, doctor_id=doctor_id, appt_id=appt_id_arg)

    if not ok_all:
        st.error(msg_all)

    # ---------- Metrics ----------
    total = len(rows_all)
    upcoming_count = len(rows_up)
    completed_count = sum(1 for r in rows_all if (r.get("status") or "").lower() == "completed")
    cancelled_count = sum(1 for r in rows_all if (r.get("status") or "").lower() == "cancelled")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", total)
    m2.metric("Upcoming", upcoming_count)
    m3.metric("Completed", completed_count)
    m4.metric("Cancelled", cancelled_count)

    st.divider()

    # Helper to reorder columns nicely for display
    def _display_rows(rows):
        ordered = []
        for r in rows:
            ordered.append({
                "Appt ID":     r.get("appt_id", ""),
                "Date":        str(r.get("date", "")),
                "Time":        str(r.get("time", "")),
                "Patient":     r.get("patient_name", ""),
                "Patient ID":  r.get("patient_id", ""),
                "Doctor":      r.get("doctor_name", ""),
                "Doctor ID":   r.get("doctor_id", ""),
                "Status":      r.get("status", ""),
                "Remark":      r.get("remark", ""),
            })
        return ordered

    # ---------- Upcoming table ----------
    st.markdown("### ⏭️ Upcoming")
    if rows_up:
        st.dataframe(
            _display_rows(rows_up)[:25], use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming appointments under current filters.")

    st.divider()

    # ---------- All appointments table ----------
    st.markdown("### 📋 All Appointments")
    # list() sorts ascending by datetime; for "All" it's often nicer newest first:
    rows_all_desc = list(reversed(rows_all))
    if rows_all_desc:
        st.dataframe(_display_rows(rows_all_desc), use_container_width=True, hide_index=True)
    else:
        st.info("No appointments match your filters.")

    st.divider()

    # ---------- Quick update (admin-permitted) ----------
    if rows_all_desc:
        with st.expander("✏️ Quick update status"):
            target_id = st.selectbox(
                "Select appointment",
                [r["appt_id"] for r in rows_all_desc],
                key="adm_appt_update_id",
            )
            new_status = st.selectbox(
                "New status",
                ["scheduled", "booked", "rescheduled", "cancelled", "completed", "no-show", "pending"],
                key="adm_appt_update_status",
            )
            new_remark = st.text_input("Remark (optional)", key="adm_appt_update_remark")

            if st.button("Update", type="primary", key="adm_appt_update_btn"):
                ok_u, msg_u, _ = apptm.update(
                    manager,
                    "admin",
                    actor_username,
                    target_id,
                    status=new_status,
                    remark=new_remark if new_remark else None,
                )
                if ok_u:
                    st.success(msg_u)
                    st.rerun()
                else:
                    st.error(msg_u)
    if rows_all_desc:
        with st.expander("📄 Export appointment report"):
            export_id = st.selectbox(
                "Select appointment to export",
                    [r["appt_id"] for r in rows_all_desc],
                    key="adm_appt_export_id",
                )
            if st.button("Generate report", key="adm_appt_export_btn"):
                    ok_x, msg_x, file_path = apptm.export_report("admin", actor_username, export_id)
                    if ok_x and file_path:
                        try:
                            # Provide a download button
                            with open(file_path, "rb") as fbin:
                                data_bytes = fbin.read()
                            st.success(msg_x)
                            st.download_button(
                                label=f"Download {export_id}.txt",
                                data=data_bytes,
                                file_name=f"{export_id}.txt",
                                mime="text/plain",
                                key="adm_appt_export_dl",
                            )
                        except Exception as e:
                            st.warning(f"Report created but could not be loaded: {e}")
                    else:
                        st.error(msg_x)