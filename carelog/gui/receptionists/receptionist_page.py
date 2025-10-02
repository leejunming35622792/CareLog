import streamlit as st

def dashboard():
    st.write("This is the Dashboard")

def receptionist_page(Manager):
    # Variables
    global manager
    manager = Manager
    global username
    username = st.session_state.username
    tabs = ["Dashboard", "1", "2", "3"]

    # Session state
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.title(f"CareLog Dashboard - Welcome {username}")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)
    st.subheader("TBC")

    if option == "Dashboard":
        dashboard()
    elif option == "1":
        st.write("This is the Profile Page")
    elif option == "2":
        st.write("This is the Records Page")
    elif option == "3":
        st.write("This is the Appointments Page")

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True