from main_dashboard import launch
from login_gui import register
from app.schedule import ScheduleManager
import streamlit as st

# --------------- Login -----------------
def login_page():
    st.set_page_config(layout="wide", page_title="Music School Management System")

    # Create sidebar title
    st.sidebar.title("MSMS Navigation")

    # Create sidebar menu option
    option = st.sidebar.radio("Select", ["Register Account", "Account Login", "Staff Login"])

    if option == "Register Account":
        register()
    elif option == "Account Login":
        pass
    elif option == "Staff Login":
        launch()

# ---------------------------------------