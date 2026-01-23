import streamlit as st
from app.utils import setup_logging, log_event
from gui.login.login_page import login_page

# To start the program and call 'login_page'
def main():
    st.set_page_config(page_title="CareLog", layout="wide")
    
    if "logging_initialized" not in st.session_state:
        # Setup logging once
        setup_logging("data/audit.log")
        # Test and output logging
        log_event("System startup complete", "INFO")
        st.session_state.logging_initialized = True

    login_page()

if __name__ == "__main__":
    main()