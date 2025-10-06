# Super class for other user classes
# Common fields as below
import datetime
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
    def get_next_id(role):
        from app.schedule import ScheduleManager
        sc = ScheduleManager()

        role = role.lower()
        if role == "patient":
            return f"P{sc.next_patient_id:04d}"
        elif role == "doctor":
            return f"D{sc.next_doctor_id:04d}"
        elif role == "nurse":
            return f"N{sc.next_nurse_id:04d}"
        elif role == "receptionist":
            return f"R{sc.next_receptionist_id:04d}"
        elif role == "admin":
            return f"A{sc.next_admin_id:04d}"
        else:
            raise ValueError(f"Invalid role: {role}")
    
    def create_user(self, manager, role, username, password, user_id, date):
        """Register new user"""
        if not all([username, password]):
            utils.log_event(f"Failed to register {role}: Details missing.", "ERROR")
            return False, "Username and password required", None
        
        # Check username duplicates
        all_usernames = [u.username for group in [
            manager.patients,
            manager.doctors,
            manager.nurses,
            manager.receptionists,
            manager.admins
        ] for u in group]

        if username in all_usernames:
            return False, "Username already in used", None
        
        # Password Validation
        if len(password) < 8:
            return False, "Password must be at least 8 characters", None
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter", None
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number", None

        # create account in auth_manager
        manager.create_account(role, user_id, username, password, date)

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

    # def update_patient_detail(manager, username, new_password, new_name, new_gender, new_address, new_email, new_contact_num, new_remark):
    #     from app.schedule import ScheduleManager
    #     manager = ScheduleManager()
    #     patient = next((p for p in manager.patients if p.username == username), None)
    #     if patient is None: #Check if patient list empty or no
    #         return False
        
    #     if new_password:
    #         patient.password = new_password
    #     if new_name:
    #         patient.name = new_name
    #     if new_gender:
    #         patient.gender = new_gender
    #     if new_address:
    #         patient.address = new_address
    #     if new_email:
    #         patient.email = new_email
    #     if new_contact_num:
    #         patient.contact_num = new_contact_num
    #     if new_remark:
    #         patient.p_remark = new_remark
        
    #     manager._save_data()
    #     return True
    
    # def add_doctor_personal_info(self,username,password,name,staff_id,contact_num,address,gender,date_of_birth):
    #     doctor=next((d for d in self.doctors if d.username==username), None)
    #     if doctor is None:
    #         return False, "Doctor Not Found", None 
    #     if doctor.password != password:
    #         return False, "Incorrect Password", None
    #     if name:
    #         doctor.name = name
    #     if contact_num:
    #         doctor.contact_num = contact_num
    #     if address:
    #         doctor.address = address
    #     if gender:
    #         doctor.gender = gender
    #     if date_of_birth:
    #             doctor.date_of_birth = date_of_birth
    #     self._save_data()
    #     return True, "Personal information added successfully"

    # def update_doctor_details(self,username,new_password,new_name,new_gender,new_address,new_email, new_contact_num,new_department,new_speciality):
    #     doctor=next((d for d in self.doctors if d.username==username),None)
    #     if doctor is None:
    #         return False
    #     if new_password:
    #         doctor.password = new_password
    #     if new_name:
    #         doctor.name = new_name
    #     if new_gender:
    #         doctor.gender = new_gender
    #     if new_address:
    #         doctor.address = new_address
    #     if new_email:
    #         doctor.email = new_email
    #     if new_contact_num:
    #         doctor.contact_num = new_contact_num
    #     if new_speciality:
    #         doctor.speciality = new_speciality
    #     if new_department:
    #         doctor.department = new_department

    #     self._save_data()
    #     return True
    
    # def update_doctor_limited_info(self, username: str, new_contact_num: str | None = None, new_address: str | None = None):
    #     doc = self.get_doctor_by_username(username)
    #     if doc is None:
    #         return False, "Doctor not found"
    #     if not doc.update_contact(contact=new_contact_num, address=new_address):
    #         return False, "No fields to update"
    #     self._save_data()
    #     return True, "Updated successfully"
    
    # def update_nurse_details(self, username, new_password=None, new_name=None, new_gender=None, new_address=None, new_email=None, new_contact_num=None, new_department=None, new_speciality=None):
    #     nurse = next((n for n in self.nurses if n.username == username), None)
    #     if nurse is None:
    #         return False
    #     if new_password: nurse.password = new_password
    #     if new_name: nurse.name = new_name
    #     if new_gender: nurse.gender = new_gender
    #     if new_address: nurse.address = new_address
    #     if new_email: nurse.email = new_email
    #     if new_contact_num: nurse.contact_num = new_contact_num
    #     if new_department: nurse.department = new_department
    #     if new_speciality: nurse.speciality = new_speciality
    #     self._save_data()
    #     return True