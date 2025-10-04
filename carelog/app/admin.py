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

    def register_new_receptionist(username, password, name, gender, address, email, contact):
        from app.schedule import ScheduleManager
        from app.receptionist import ReceptionistUser
        if not name or not password or not username or not gender or not address or not email or not contact:
            utils.log_event(f"Failed to register student: Details missing", "ERROR")
            return False, "Details required", None
        if "@" not in email:
            return False, "Invalid email address", None
        if any(r.email == email for r in ScheduleManager.receptionists):
            return False, "Email already registered", None
        receptionist_id = f"S{ScheduleManager.next_receptionist_id:04d}"
        date_joined = datetime.datetime.now().isoformat()
        receptionist = ReceptionistUser(receptionist_id, username, password, name, gender, address, email, contact, date_joined)
        ScheduleManager.receptionists.append(receptionist)
        ScheduleManager.next_receptionist_id += 1
        ScheduleManager.save()
        utils.log_event(f"Receptionist {name} registered with ID {receptionist_id}", "INFO")
        return True, f"Welcome {name}! Your ID is {receptionist_id}.", receptionist

    """System Management"""
    def view_users(self):
        pass

    def view_all_logs(self):
        pass

    def view_reg_logs(self):
        pass

    """Data Management"""
    def view_logs(self, n=10):
        """Return last n logs for UI display"""
        return utils.get_recent_logs(n)

    def backup(self):
        from app.schedule import ScheduleManager
        ScheduleManager.BackupSystem()