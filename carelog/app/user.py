# Super class for other user classes
# Common fields as below
import datetime
from manager.auth_manager import AuthManager
import app.utils as utils

class User:
    def __init__(self, username, password, name, gender, address, email, contact_num, date_joined):
        self.username = username
        self.password = password
        self.name = name
        self.gender = gender
        self.address = address
        self.email = email
        self.contact_num = contact_num
        self.date_joined = date_joined

    @staticmethod
    def get_next_id(manager, role):
        role = role.lower()
        if role == "patient":
            return f"P{manager.next_patient_id:04d}"
        elif role == "doctor":
            return f"D{manager.next_doctor_id:04d}"
        elif role == "nurse":
            return f"N{manager.next_nurse_id:04d}"
        elif role == "receptionist":
            return f"R{manager.next_receptionist_id:04d}"
        elif role == "admin":
            return f"A{manager.next_admin_id:04d}"
        else:
            raise ValueError(f"Invalid role: {role}")
    
    @staticmethod
    def create_user(manager, role, user_id, username, password, name, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        """Register new user"""
        if not all([username, password]):
            utils.log_event(f"Failed to register {role}: Details missing.", "ERROR")
            return False, "Username and password required", None
        
        # Username Validation


        if username in all_usernames:
            return False, "Username already in used", None
        
        # Password Validation
        if len(password) < 8:
            return False, "Password must be at least 8 characters", None
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter", None
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number", None
        
        # Check if blank
        fields = {
            "Name": name,
            "Gender": gender,
            "Address": address,
            "Email": email,
            "Contact Number": contact_num,
        }

        for field, value in fields.items():
            if not value.strip():
                return False, f"{field} cannot be empty", None
            
        if role in ["doctor", "nurse"]:
            if not speciality:
                return False, "Speciality cannot be empty", None
            if not department:
                return False, "Department cannot be empty", None
            if role == "nurse" and not with_doctor:
                return False, "'with_doctor' cannot be empty", None

        # create account in auth_manager
        AuthManager.create_account(role, user_id, username, password, date)

        # Capitalize turns the first letter to upper, remaining be lower
        utils.log_event(f"{role.capitalize()} {username} registered with ID {user_id}", "INFO")
        return True, f"{role.capitalize()} created successfully! ID: {user_id}", None
    
    # Update detail
    def update_profile(self, user_id, role, password, name, gender, address, email, contact_num, date_of_birth, department, speciality):
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        role = role.lower()
        
        # Get correct user list
        user_list = getattr(sc, f"{role}s")
        if user_list is None:
            return False, f"Invalid role: {role}"
        
        # Find target user
        user = next((u for u in user_list if getattr(u, f"{role[0]}_id", None) == user_id), None)
        if user is None:
            return False, f"No user found with ID {user_id}"
        
        # Update field
        if password:
            user.password = password
        if name:
            user.name = name
        if gender:
            user.gender = gender
        if address:
            user.address = address
        if email:
            from manager.auth_manager import AuthManager
            success, message, _ = AuthManager.check_email_validation(email)
            if success:
                user.email = email
        if contact_num:
            user.contact_num = contact_num
        if date_of_birth:
            user.date_of_birth = date_of_birth

        if role == "doctor":
            if speciality:
                user.speciality = speciality
            if department:
                user.department = department

        sc.save()
        utils.log_event(f"{role.capitalize()} '{user.username}' (ID: {user_id}) profile updated", "INFO")

        return True, f"{role.capitalize()} profile updated successfully", user
    
    def update_new_profile(self, user_id, role, username, new_password, new_name, new_gender, new_address, new_email, new_contact_num, new_department, new_speciality):
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        role = role.lower()
        
        # Get correct user list
        user_list = getattr(sc, f"{role}s")
        if user_list is None:
            return False, f"Invalid role: {role}"
        
        # Find target user
        user = next((u for u in user_list if getattr(u, f"{role[0]}_id", None) == user_id), None)
        if user is None:
            return False, f"No user found with ID {user_id}"
        
        # Update field
        if new_password:
            user.password = new_password
        if new_name:
            user.name = new_name
        if new_gender:
            user.gender = new_gender
        if new_address:
            user.address = new_address
        if new_email:
            from manager.auth_manager import AuthManager
            success, message, _ = AuthManager.check_email_validation(new_email)
            if success:
                user.email = new_email
        if new_contact_num:
            user.contact_num = new_contact_num

        # Specific details for role (Can be added more)
        if role == "doctor":
            if new_speciality:
                user.speciality = new_speciality
            if new_department:
                user.department = new_department

        sc.save()
        utils.log_event(f"{role.capitalize()} '{user.username}' (ID: {user_id}) profile updated", "INFO")

        return True, f"{role.capitalize()} profile updated successfully", user

    