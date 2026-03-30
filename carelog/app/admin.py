import datetime
import app.utils as utils
from app.user import User
from helper_manager.appointment_manager import AppointmentManager
# the admin user class inheriting from the base user class
class AdminUser(User):
    def __init__(self, a_id: str, username: str, password: str, name: str, bday: str, gender: str, address: str, email: str, contact_num: str, date_joined: str):
        self.a_id = a_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)
# registers a new users based on its role and details provided
    """Account Management"""
    def register_user(self, role, username, password, name, bday, gender, address, email, contact):
        """
        Admin creates any user (including admin)
        """
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        # Validation
        if not all([username, password]):
            utils.log_event(f"Failed to register {role}: Missing details", "ERROR")
            return False, "All fields are required", None

        # Gather all usernames and emails across all roles
        all_usernames = [
            u.username for group in [
                sc.patients, sc.doctors, sc.nurses,
                sc.receptionists, sc.admins
            ] for u in group
        ]

        if username in all_usernames:
            utils.log_event(f"Failed to register {role}: Username in used", "ERROR")
            return False, "Username already in used", None

        # Get next ID for the role
        next_id = User.get_next_id(sc, role)
        date_joined = datetime.datetime.now().isoformat()

        # Create new user using central factory in user_manager
        success, message, new_user = User.create_user(sc, role, next_id, username, password, name, bday, gender, address, email, contact, date_joined)

        if success:
            utils.log_event(f"Admin created new {role} account {username} ({next_id})", "INFO")
            return True, f"{role.capitalize()} '{username}' created successfully with ID {next_id}", new_user
        else:
            utils.log_event(f"Failed to create new {role} account", "ERROR")
            return False, message, None
    # removes a user based on the role and its user ID provided as the argument
    def remove_user(self, role, user_id):
        """Remove user by role and id"""
        from app.schedule import ScheduleManager
        sc = ScheduleManager()

        user_list = getattr(sc, f"{role}s")

        # Search by ID
        user_to_remove = None
        for user in user_list:
            if getattr(user, f"{role[0]}_id", None) == user_id:
                user_to_remove = user
                break
        # User not found
        if not user_to_remove:
            utils.log_event(f"Failed to remove {role}: {user_id} not found", "WARNING")
            return False, f"{role.capitalize()} not found."

        # Remove user
        user_list.remove(user_to_remove)
        sc.save()

        utils.log_event(f"Admin removed {role} '{user_to_remove.user_id}' ({user_id})", "INFO")
        return True, f"{role.capitalize()} '{user_to_remove.user_id}' removed successfully."
    # retrieves the appointment details based on the username and manager provided
    def get_appointment(self, username, manager):
        appt_manager = AppointmentManager(manager)
        return appt_manager.list(manager, "admin", username, scope="own", upcoming_only=False, date=None, status=None, patient_id=None, doctor_id=None, appt_id=None)
    # retrieves upcoming appointment details based on the username and manager provided
    def upcoming_appointment(self, username, manager):
        appt_manager = AppointmentManager(manager)
        return appt_manager.list(manager, "admin", username, scope="own", upcoming_only=True, date=None, status=None, patient_id=None, doctor_id=None, appt_id=None)
    # views recent system logs
    """System Management"""
    def view_all_logs(self, n=20):
        """Return last n system logs"""
        return utils.get_recent_logs(n)
    # performs a system backup
    """Data Management"""
    def backup(self):
        utils.BackupSystem()
        utils.log_event("System backup completed", "INFO")