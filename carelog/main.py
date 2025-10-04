from app.utils import setup_logging, log_event
from gui.login.login_page import login_page

# To start the program and call 'login_page'
def main():
    # Setup logging once
    setup_logging("data/audit.log")
    # test and output logging
    log_event("System startup complete", "INFO")
    
    login_page()

if __name__ == "__main__":
    main()