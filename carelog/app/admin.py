import datetime
import app.utils as utils
from app.user import User

class AdminUser(User):
    def __init__(self, a_id, username, password, name, bday, gender, address, email, contact_num, date_joined):
        self.admin_password = "admin"
        self.a_id = a_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)

    """Account Management"""
    def register_user(self, role, username, password):
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
            return False, "Username already in used", None

        # Get next ID for the role
        next_id = User.get_next_id(role)
        date_joined = datetime.datetime.now().isoformat()

        # Create new user using central factory in user_manager
        success, message, new_user = User.create_user(
            role, next_id, username, password, date_joined)

        if success:
            utils.log_event(f"Admin created new {role} account {username} ({next_id})", "INFO")
            return True, f"{role.capitalize()} '{username}' created successfully with ID {next_id}", new_user
        else:
            return False, message, None

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

        if not user_to_remove:
            utils.log_event(f"Failed to remove {role}: {user_id} not found", "WARNING")
            return False, f"{role.capitalize()} not found."

        # Remove user
        user_list.remove(user_to_remove)
        sc.save()
        utils.log_event(f"Admin removed {role} '{user_to_remove.user_id}' ({user_id})", "INFO")

        return True, f"{role.capitalize()} '{user_to_remove.user_id}' removed successfully."

    """System Management"""
    def view_all_logs(self, n=20):
        """Return last n system logs"""
        return utils.get_recent_logs(n)

    """Data Management"""
    def backup(self):
        utils.BackupSystem()
        utils.log_event("System backup completed", "INFO")