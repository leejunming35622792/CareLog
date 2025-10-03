from app.schedule import ScheduleManager
from app.user import User

class AdminUser(User):
    def __init__(self, a_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.admin_password = "admin"
        self.a_id = a_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        self._load_data()

    """Account Management"""
    def account_managemnet(self):
        pass

    def create_account(self):
        name = input("Name: ")
        password = input("Password: ")
        username = input("Username: ")
        
        pass

    """System Management"""
    def view_users(self):
        pass

    def view_all_logs(self):
        pass

    def view_reg_logs(self):
        pass

    """Data Management"""
    def backup(self):
        ScheduleManager.BackupSystem()
        pass