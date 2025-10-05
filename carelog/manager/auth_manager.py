import re
from app.patient import PatientUser
from app.doctor import DoctorUser
from app.nurse import NurseUser
from app.receptionist import ReceptionistUser
from app.admin import AdminUser
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
            return True, user
        return False, None
        
        # Map each role to its user-password dict
        # accounts = {
        #     "Patient": {p.username: p.password for p in self.patients},
        #     "Doctor": {d.username: d.password for d in self.doctors},
        #     "Nurse": {n.username: n.password for n in self.nurses},
        #     "Receptionist": {r.username: r.password for r in self.receptionists},
        #     "Admin": {a.username: a.password for a in self.admins},
        # }

        # # Check if role exists
        # if staff not in accounts:
        #     return False

        # acc = accounts[staff]

        # # Verify username and password
        # if username in acc and acc[username].strip() == password:
        #     return staff
        # else:
        #     return False

    def create_account(self, role, user_id, username, password, date):
        user_obj = self._user(role, user_id, username, password, date)
        role = role.lower()
        if role == "patient":
            self.patients.append(user_obj)
            self.next_patient_id += 1
        elif role == "doctor":
            self.doctors.append(user_obj)
            self.next_doctor_id += 1
        elif role == "nurse":
            self.nurses.append(user_obj)
            self.next_nurse_id += 1
        elif role == "receptionist":
            self.receptionists.append(user_obj)
            self.next_receptionist_id += 1
        elif role == "admin":
            self.admins.append(user_obj)
            self.next_admin_id += 1
        self.system.save()

    def _user(self, role, user_id, username, password, date):
        """Create correct role object"""
        role = role.lower()
        if role == "patient":
            from app.patient import PatientUser
            return PatientUser(user_id, username, password, "", "", "", "", "", date, [], "")
        elif role == "doctor":
            from app.doctor import DoctorUser
            return DoctorUser(user_id, username, password, "", "", "", "", "", date, "", "")
        elif role == "nurse":
            from app.nurse import NurseUser
            return NurseUser(user_id, username, password, "", "", "", "", "", date, "", "", "")
        elif role == "receptionist":
            from app.receptionist import ReceptionistUser
            return ReceptionistUser(user_id, username, password, "", "", "", "", "", date)
        elif role == "admin":
            from app.admin import AdminUser
            return AdminUser(user_id, username, password, "", "", "", "", "", date)
        else:
            raise ValueError(f"Invalid role type: {role}")

    def check_email_validation(self, email):
        if not email:
            return False, "Email cannot be empty", None
        if "@" not in email:
            return False, "Not a valid email", None
        
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        match = re.match(pattern, email)
        if not match:
            return False, "Invalid email format", None
    
        # Extract the domain part after the last dot
        domain_part = match.group(1).lower()
        # Get the list of valid TLDs
        valid_domain = utils.domain_list()
        # Check if the email's TLD matches any in the list
        for domain in valid_domain:
            if domain_part.endswith(domain):
                return True, "Valid email format", None

        return False, f"Invalid top-level domain: {domain}", None

# def login_doctor(self,username,password):
#         doctor=next((d for d in self.doctors if d.username==username))
#         if doctor is None:
#             return False, "Doctor Not Found ", None
#         if doctor.password != password:
#             return False, "Incorrect Password"
        
#         return True, "Logic Successful", doctor