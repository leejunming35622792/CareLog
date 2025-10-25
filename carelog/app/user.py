# Super class for other user classes
# Common fields as below
import re, datetime
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
        role = str(role.lower())
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
        auth = AuthManager(manager)

        errors = []

        bday = bday.isoformat()

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
                errors.append("Speciality cannot be empty")
                return False, errors, None
            if not department:
                errors.append("Department cannot be empty")
                return False, errors, None
            if role == "nurse" and not with_doctor:
                errors.append("'with_doctor' cannot be empty")
                return False, errors, None
            
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
        valid, msg, _ = auth.check_email_validation(email)
        if valid == False:
            errors.append(msg)

        # Contact Number Validation
        num_valid, msg, _ = auth.check_contact_validation(contact_num)
        if num_valid == False:
            errors.append(msg)
        
        if errors:
            return False, errors, None
        else:
            # create account in auth_manager
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
    
    @staticmethod
    def update_profile(manager, user_id, role, username, password, name, bday, gender, address, email, contact_num, remark, department, speciality):
            role = role.lower()

            users_list = getattr(manager, f"{role}s", None)
            if users_list is None:
                return None, f"Invalid role: {role}"

            # Find target user by their role-specific ID (e.g., doctor_id, patient_id)
            role_disp = {
                "patient": "p_id",
                "doctor": "d_id",
                "nurse": "n_id",
                "receptionist": "r_id",
                "admin": "a_id"
            }

            id_attr = role_disp.get(role)
            if not id_attr:
                return None, f"Invalid role: {role}"

            user = next((u for u in users_list if getattr(u, id_attr, None) == user_id), None)

            if user is None:
                return None, f"No {role} found with ID {user_id}"

            # Update fields
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
                auth = AuthManager(manager)
                success, message, _ = auth.check_email_validation(email)
                if success:
                    user.email = email

            if contact_num: 
                user.contact_num = contact_num
            if remark: 
                user.remark = remark

            # Extra fields for doctors
            if role == "doctor":
                if speciality: 
                    user.speciality = speciality
                if department: 
                    user.department = department

            manager.save()
            utils.log_event(f"{role.capitalize()} '{user.username}' (ID: {user_id}) profile updated", "INFO")

            return user, f"{role.capitalize()}'s profile updated successfully"