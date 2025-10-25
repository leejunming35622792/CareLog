import re
import app.utils as utils

"""
Handles logics for authorisation
including create account, login and verification
"""

class AuthManager:
    def __init__(self, system):
        # System here is Schedule Manager
        self.system = system

    def check_credentials(self, role, username, password):
        users = getattr(self.system, f"{role.lower()}s", [])
        # using next to search for a user in user_list, stop when found, or return none by default if not found
        user = next((u for u in users if u.username == username and u.password == password), None)
        if user:
            return True, "Logging in...", user
        return False, "Incorrect credentials", None

    def create_account(self, manager, role, user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        # Create object
        role = role.lower()

        # Try-except to handle self._user from returning none
        try:
            user_obj = self._user(manager, role, user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor)
        except Exception as e:
            return False, f"User creation failed: {e}", None

        # Delegate adding user to ScheduleManager
        self.system.add_user(role, user_obj)
        return True, f"{role.capitalize()} account created successfully!", user_obj

    def _user(self, manager, role, user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        """Create correct role object"""
        role = role.lower()
        if role == "patient":
            from app.patient import PatientUser
            return PatientUser(user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, [], "")
        elif role == "doctor":
            from app.doctor import DoctorUser
            return DoctorUser(user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department)
        elif role == "nurse":
            from app.nurse import NurseUser
            return NurseUser(user_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor)
        elif role == "receptionist":
            from app.receptionist import ReceptionistUser
            return ReceptionistUser(user_id, username, password, name, bday, gender, address, email, contact_num, date_joined)
        elif role == "admin":
            from app.admin import AdminUser
            return AdminUser(user_id, username, password, name, bday, gender, address, email, contact_num, date_joined)
        else:
            raise ValueError(f"Invalid role type: {role}")

    def _get_next_id(self, role):
        """Ask system for the next available user ID"""
        role = role.lower()
        return getattr(self.system, f"next_{role}_id")

    def check_email_validation(self, email):
        if not email:
            return False, "Email cannot be empty", None
        if "@" not in email:
            return False, "Not a valid email", None
        
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, email):
            return False, "Invalid email format", None
    
        # Extract the domain part after the last dot
        domain_part = email.split('.')[-1].lower()
        # Get the list of valid TLDs
        valid_domain = utils.domain_list() or []
        # Check if the email's TLD matches any in the list
        for domain in valid_domain:
            if domain_part.endswith(domain.lstrip('.').lower()):
                return True, "Valid email format", None
        return False, f"Invalid top-level domain: {domain_part}", None
    
    def check_contact_validation(contact_num):
        if not contact_num:
            return False, "Missing contact number", None
        
        contact_num_format = r"^\+601[0-9]-?[0-9]{7,8}$"
        if not re.match(contact_num_format, contact_num):
            return False, f"Contact number is invalid - please include '+60' and '-'", None