import streamlit as st
import datetime, time
from app.schedule import ScheduleManager
import app.utils as utils

@st.cache_resource
def get_manager():
    return ScheduleManager()

def dashboard():
    st.write("This is the Dashboard")
    placeholder = st.empty()
    while True:
        with placeholder.container():
            col1, col2 = st.columns(2)
            col1.metric("Time", datetime.datetime.now().today())
        time.sleep(1)

def admin_page(manager):
    # Variables
    manager = get_manager()
    tabs = ["Dashboard", "Profile", "Management", "Records"]

    # guard for username/session
    username = st.session_state.get("username", "Admin")

    st.title(f"CareLog Dashboard - Welcome {username}")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)

    if option == "Dashboard":
        dashboard()
    elif option == "Profile":
        st.write("This is the Profile Page")
    elif option == "Management":
        tab1, tab2 = st.tabs(["User Management", "Appointment"])

        with tab1:
            st.subheader("User Management")
            with st.form("register_form"):
                user_type = st.selectbox("User type", ["Patient", "Doctor", "Nurse", "Receptionist"])
                name = st.text_input("Name")
                password = st.text_input("Password", type="password")
                username = st.text_input("Username")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                address = st.text_input("Address")
                email = st.text_input("Email")
                contact = st.text_input("Contact")
                submitted = st.form_submit_button("Register")
                if submitted:
                    if user_type == "Patient":
                        success, msg, _ = manager.add_account_patient(username, password)
                        # you can extend add_account_patient to accept full details later
                    elif user_type == "Doctor":
                        success = True
                        try:
                            doc = manager.add_account_doctor(username, password)
                            msg = f"Doctor created: {doc.__dict__.get('username', username)}"
                        except Exception as e:
                            success = False
                            msg = str(e)
                    elif user_type == "Nurse":
                        # implement a manager.register_new_nurse(...) if you want full details
                        success = False
                        msg = "Nurse registration not implemented in GUI yet"
                    elif user_type == "Receptionist":
                        success, msg, _ = manager.register_new_receptionist(username, password, name, gender, address, email, contact)

                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

            if st.button("Remove User", key="remove_user_button"):
                pass

        with tab2:
            st.subheader("Appointment")
            pass

        st.write("This is the Appointments Page")

    elif option == "Records":
        st.write("This is the Records Page")

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