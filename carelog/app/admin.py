import datetime
import app.utils as utils
from app.user import User

class AdminUser(User):
    def __init__(self, a_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.admin_password = "admin"
        self.a_id = a_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)

    """Account Management"""
    def account_managemnet(self):
        pass
    
    def register_user(self, role, username, password, name, gender, address, email, contact, date_joined):
        return User.create_user(role, username, password, name, gender, address, email, contact, date_joined)

    def remove_user(role, user_id):
        from app.schedule import ScheduleManager

        pass

    """System Management"""

    def view_logs(self, n=10):
        """Return last n logs for UI display"""
        return utils.get_recent_logs(n)

    """Data Management"""
    def backup(self):
        utils.BackupSystem()
        utils.log_event("System backup completed", "INFO")