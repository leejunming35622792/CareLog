import streamlit as st
import datetime, time
from app.admin import AdminUser
from app.user import User as user
import app.utils as utils
from gui.admins.admin_appt_page import appointment_page

def dashboard(manager):
    st.write("This is the Dashboard")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col1, col2 = st.columns(2)
    col1.metric("Current time", now)
    if col2.button("Refresh time"):
        st.rerun()

    st.divider()
    col3, col4, col5 = st.columns(3)
    col3.metric("Patients", len(manager.patients))
    col4.metric("Doctors", len(manager.doctors))
    col5.metric("Appointments", len(manager.appointments))

def admin_page(manager):
    current_username = st.session_state.get("username")
    admin = next((a for a in manager.admins if a.username == current_username), None)

    tabs = ["Dashboard", "Profile", "Management", "Appointments", "Records"]

    # guard for username/session
    username = st.session_state.get("username", "Admin")

    st.title(f"CareLog Dashboard - Welcome {username}")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)

    # ============================================================
    # DASHBOARD
    # ============================================================
    if option == "Dashboard":
        dashboard(manager)

    # ============================================================
    # PROFILE TAB
    # ============================================================
    elif option == "Profile":
        admin = next((a for a in manager.admins if a.username == st.session_state.username), None)

        if admin:
            st.text_input("Username", admin.username, disabled=True)
            st.text_input("Email", admin.email, disabled=True)
            st.text_input("Role", "Administrator", disabled=True)
        else:
            st.warning("No admin data found.")

    # ============================================================
    # MANAGEMENT
    # ============================================================
    elif option == "Management":
        tab1, tab2 = st.tabs(["Add User", "Remove User"])

        with tab1:
            st.subheader("User Management")
            with st.form("register_form"):
                role = st.selectbox("Select Role", ["Patient", "Doctor", "Nurse", "Receptionist", "Admin"])

                user_id = user.get_next_id(manager, role)

                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Assigned ID", user_id, disabled=True)
                with c2:
                    username = st.text_input("Username", key="reg_username")

                c3, c4 = st.columns(2)
                with c3:
                    password = st.text_input("Password", type="password", key="reg_password")
                with c4:
                    name = st.text_input("Name", key="reg_name")

                c5, c6 = st.columns(2)
                with c5:
                    bday     = st.date_input("Birthday", datetime.date(2025, 1, 1), key="reg_birthday")
                with c6:
                    gender   = st.selectbox("Gender", ["Male", "Female"], key="reg_gender")
                
                address  = st.text_input("Address", key="reg_address")
                
                c7, c8 = st.columns(2)
                with c7:
                    email    = st.text_input("Email", key="reg_email")
                with c8:
                    contact  = st.text_input("Contact", key="reg_contact")

                if st.form_submit_button("Create Account"):
                    with st.spinner("Registering..."):
                        time.sleep(1)
                    success, message, _ = admin.register_user(role, username, password, name, bday, gender, address, email, contact)

                    if success:
                        manager.save()
                        st.success(message)
                        st.toast(f"{role} account successfully created!")
                        st.rerun()
                    else:
                        utils.log_event(f"Failed registration for {role} ({username}): {message}", "ERROR")
                        st.error(message)

        with tab2:
            """Remove user by role and id"""
            st.subheader("Remove User")

            role_rm = st.selectbox("Select Role", ["Patient", "Doctor", "Nurse", "Receptionist", "Admin"])
            user_list = getattr(manager, f"{role_rm.lower()}s", [])

            if not user_list:
                st.info(f"No {role_rm} found")
            else:
                user_display = [f"{u.username} ({getattr(u, f'{role_rm[0].lower()}_id', 'N/A')})" for u in user_list]
                selected_user = st.selectbox(f"Select {role_rm} to remove", user_display)
                if st.button("Confirm Remove", type="primary"):
                    user_id = selected_user.split("(")[1].strip(")")
                    success, message = admin.remove_user(role_rm, user_id)
                    if success:
                        st.success(message)
                        st.toast(message)
                        st.rerun()
                    else:
                        st.error(message)

    elif option == "Appointments":
        appointment_page(manager)
        utils.log_event(f"Viewed all appointments and upcoming appointments", "INFO")

    # ============================================================
    # RECORDS
    # ============================================================
    elif option == "Records":
        st.write("This is the Records Page")
        st.header("📁 Records")

        if hasattr(manager, "records"):
            if manager.records:
                st.dataframe([r.__dict__ for r in manager.records], use_container_width=True, hide_index=True)
            else:
                st.info("No records available.")
        else:
            st.warning("Records not found in manager.")

def admin_logs_page():
    """Function to view logs"""
    st.title("System Logs")

    # Options
    search_term = st.text_input("Search Logs")
    level_filter = st.selectbox("Filter by level", ["All", "INFO", "WARNING", "ERROR"])
    # slider, prompt, min, max, value
    n = st.slider("Show last N logs", 5, 50, 10)

    # Get Logs
    logs = utils.get_recent_logs(n)

    # Filters
    if level_filter != "All":
        logs = [log for log in logs if log['level'] == level_filter]
    if search_term:
        logs = [log for log in logs if search_term.lower() in log["event"].lower()]
    
    # Display Logs
    if logs:
        for log in logs:
            st.write(f"[{log['timestamp']}] {log['level']} - {log['event']}")
    else:
        st.info("No logs found matching your filters.")

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True