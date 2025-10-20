# Super class for other user classes
# Common fields as below
import datetime
import re
from helper_manager.auth_manager import AuthManager
import app.utils as utils

class User:
    def __init__(self, username, password, name, bday, gender, address, email, contact_num, date_joined):
        self.username = username
        self.password = password
        self.name = name
        self.bday = bday
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
    def create_user(manager, role, user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        """Register new user & Check Blank"""

        errors = []

        # Check if any fields are blank
        fields = {
            "Name": name,
            "Gender": gender,
            "Address": address,
            "Birthday": bday,
            "Email": email,
            "Contact Number": contact_num,
        }

        for field, value in fields.items():
            if not value.strip():
                errors.append(f"{field} cannot be empty")
        
        if errors:
            return False, errors, None
            
        if role in ["doctor", "nurse"]:
            if not speciality:
                return False, "Speciality cannot be empty", None
            if not department:
                return False, "Department cannot be empty", None
            if role == "nurse" and not with_doctor:
                return False, "'with_doctor' cannot be empty", None
            
        if not all([username, password]):
            utils.log_event(f"Failed to register {role}: Details missing.", "ERROR")
            errors.append("Username and password required")
        
        # Password Validation
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        # Email Validation
        email_format = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_format, email):
            errors.append("Email is invalid - please include the top-domain level")

        # Contact Number Validation
        contact_num_format = r"^\+601[0-9]-?[0-9]{7,8}$"
        if not re.match(contact_num_format, contact_num):
            errors.append("Contact number is invalid - please include '+60' and '-'")
        
        if errors:
            return False, errors, None
        else:
            # create account in auth_manager
            auth = AuthManager(manager)

            success, msg, user_obj = auth.create_account(
                manager, 
                role, 
                user_id, username, password, 
                name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor
            )

            if not success:
                # Capitalize turns the first letter to upper, remaining be lower
                utils.log_event(f"")
                return False, msg, None
            utils.log_event(f"{role.capitalize()} {username} registered with ID {user_id}", "INFO")
            return True, msg, user_obj
    
    # Update detail
    def update_profile(self, user_id, role, password, name, bday, gender, address, email, contact_num, date_of_birth, department, speciality):
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        role = role.lower()
        
        # Get correct user list
        # user_list = getattr(sc, f"{role}s")
        # if user_list is None:
        #     return False, f"Invalid role: {role}"
        
        # Find target user
        user = next((u for u in sc.patients if getattr(u, f"{role[0]}_id", None) == user_id), None)
        if user is None:
            return False, f"No user found with ID {user_id}"
        
        # Update field
        if password:
            user.password = password
        if name:
            user.name = name
        if bday:
            user.bday = bday
        if gender:
            user.gender = gender
        if address:
            user.address = address
        if email:
            from helper_manager.auth_manager import AuthManager
            auth = AuthManager(sc)
            success, message, _ = auth.check_email_validation(email)
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