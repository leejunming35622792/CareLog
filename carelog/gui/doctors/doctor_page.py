import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from gui.doctors import doctor_remark_page
from gui.doctors import doctor_medication_page
from gui.doctors.doctor_dashboard import dashboard
from gui.doctors.doctor_profile import profile_page
from gui.doctors.doctor_view_records_page import patient_records_page
from gui.doctors.doctor_appt_page import appointments_page
from gui.doctors.doctor_shift_page import shift_page
from gui.doctors.doctor_remark_page import remarks_page
from gui.doctors.doctor_medication_page import medication_page

def search_and_select_profile_ui(manager):
    role_map = {
        "patient": (manager.patients, "p_id"),
        "doctor": (manager.doctors, "d_id"),
        "nurse": (manager.nurses, "n_id"),
        "receptionist": (manager.receptionists, "r_id"),
    }

    st.subheader("Search Profiles")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        role = st.selectbox("Role", list(role_map.keys()))
    with col2:
        name_query = st.text_input("Name (partial ok)")
    with col3:
        trigger = st.button("Search", use_container_width=True)

    if not trigger:
        return False, None, None

    items, id_attr = role_map[role]
    nq = name_query.strip().lower()
    matches = [o for o in items if nq in getattr(o, "name", "").lower()]

    if not matches:
        st.warning(f"No {role} found matching '{name_query}'.")
        return False, None, None

    rows, idx = [], {}
    for o in matches:
        oid = getattr(o, id_attr)
        rows.append({
            "ID": oid,
            "Name": getattr(o, "name", ""),
            "Gender": getattr(o, "gender", ""),
            "Email": getattr(o, "email", ""),
            "Contact": getattr(o, "contact_num", ""),
            "Department": getattr(o, "department", ""),
            "Speciality": getattr(o, "speciality", ""),
            "Joined": getattr(o, "date_joined", ""),
        })
        idx[oid] = o

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    sel_id = st.selectbox(f"Select {role.capitalize()} ID", df["ID"].tolist())
    view = st.button("View profile", use_container_width=True)

    if view and sel_id:
        selected = idx.get(sel_id)
        if selected:
            st.subheader(f"{role.capitalize()} Profile: {sel_id}")
            for k, v in selected.__dict__.items():
                if k == "password":
                    continue
                st.write(f"**{k}**: {v}")
            return True, selected, role

    return False, None, None

def doctor_page(_Manager):
    manager = st.session_state.manager
    username = st.session_state.username

    tabs = ["Dashboard", "Profile", "Patient Records", "Medications", "Appointments", "Shift", "Remarks"]

    if st.session_state.get("logout_triggered"):
        st.session_state.logout_triggered = False
        st.rerun()

    st.sidebar.title("CareLog Navigation")
    st.sidebar.write(f"@{username}")
    st.sidebar.divider()
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.divider()
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)

    if option == "Dashboard":
        dashboard(manager, username)
    elif option == "Profile":
        profile_page(manager, username)
    elif option == "Patient Records":
        patient_records_page(manager, username)
    elif option == "Medications":
        medication_page(manager, username)
    elif option == "Appointments":
        appointments_page(manager, username)
    elif option == "Shift":
        shift_page(manager)
    elif option == "Remarks":
        remarks_page(manager, username)


def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logout_triggered = True
    st.session_state.get_user_detail = ""
