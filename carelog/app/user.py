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

    # Login Page - Create Account first
    def get_next_id(self, role):
        """Generate the next unique ID based on ScheduleManager counters."""
        from app.schedule import ScheduleManager as sc
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
    
    def create_user(self, role, username, password, user_id, date):
        """Register new user"""
        from app.schedule import ScheduleManager as sc
        if not all([username, password]):
            utils.log_event(f"Failed to register {role}: Details missing.", "ERROR")
            return False, "Username and password required", None
        
        # Check duplicates
        all_usernames = [u.username for group in [
            sc.patients,
            sc.doctors,
            sc.nurses,
            sc.receptionists,
            sc.admins
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
        
        # Create object using function
        user_obj = self._user(role, user_id, username, password, date)

        # Add object to list
        if role == "patient":
            sc.patients.append(user_obj)
            sc.next_patient_id += 1
        elif role == "doctor":
            sc.doctors.append(user_obj)
            sc.next_doctor_id += 1
        elif role == "nurse":
            sc.nurses.append(user_obj)
            sc.next_nurse_id += 1
        elif role == "receptionist":
            sc.receptionists.append(user_obj)
            sc.next_nurse_id += 1
        elif role == "admin":
            sc.admins.append(user_obj)
            sc.next_admin_id += 1

        # Capitalize turns the first letter to upper, remaining be lower
        utils.log_event(f"{role.capitalize()} {username} registered with ID {user_id}", "INFO")
        return True, f"{role.capitalize()} created successfully! ID: {user_id}", user_obj
    
    def _user(self, role, user_id, username, password, date):
        """Create correct role object"""
        role = role.lower()
        if role == "patient":
            from app.patient import PatientUser
            return PatientUser(user_id, username, password, "", "", "", "", "", date, [], "")
        elif role == "doctor":
            from app.doctor import DoctorUser
            return DoctorUser(user_id, username, password, "", "", "", "", "", date)
        elif role == "nurse":
            from app.nurse import NurseUser
            return NurseUser(user_id, username, password, "", "", "", "", "", date)
        elif role == "receptionist":
            from app.receptionist import ReceptionistUser
            return ReceptionistUser(user_id, username, password, "", "", "", "", "", date)
        elif role == "admin":
            from app.admin import AdminUser
            return AdminUser(user_id, username, password, "", "", "", "", "", date)
        else:
            raise ValueError(f"Invalid role type: {role}")

    # def add_account_patient(self, username, password):
    #     joined_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     new_patient = PatientUser.create_acc(self.next_patient_id, username, password, str(joined_date))
    #     self.patients.append(new_patient)
    #     self.next_patient_id += 1
    #     return True
    
    # def register_doctor(self, email, password):

    #     if not email or "@" not in email:
    #         return False, "Invalid email address", None
        
    #     if any(d.email == email for d in self.doctors):
    #         return False, "Email already registered", None
        
    #     if not password or len(password) < 6:
    #         return False, "Password must be at least 6 characters", None
        
    #     joined_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     new_doctor = DoctorUser(
    #         self.next_doctor_id,
    #         email,
    #         password,
    #         "",
    #         "",
    #         "",
    #         email,
    #         "",
    #         joined_date,
    #         "",
    #         ""
    #     )
        
    #     self.doctors.append(new_doctor)
    #     doctor_id = self.next_doctor_id
    #     self.next_doctor_id += 1
    #     self._save_data()
        
    #     return True, "Doctor registered successfully", doctor_id
    

    #Update detail
    def update_patient_detail(self, username, new_password, new_name, new_gender, new_address, new_email, new_contact_num, new_remark):
        patient = next((p for p in self.patients if p.username == username), None)
        if patient is None: #Check if patient list empty or no
            return False
        if new_password:
            patient.password = new_password
        if new_name:
            patient.name = new_name
        if new_gender:
            patient.gender = new_gender
        if new_address:
            patient.address = new_address
        if new_email:
            patient.email = new_email
        if new_contact_num:
            patient.contact_num = new_contact_num
        if new_remark:
            patient.p_remark = new_remark
            
        self._save_data()
        return True
    
    def add_doctor_personal_info(self,username,password,name,staff_id,contact_num,address,gender,date_of_birth):
        doctor=next((d for d in self.doctors if d.username==username), None)
        if doctor is None:
            return False, "Doctor Not Found", None 
        if doctor.password != password:
            return False, "Incorrect Password", None
        if name:
            doctor.name = name
        if contact_num:
            doctor.contact_num = contact_num
        if address:
            doctor.address = address
        if gender:
            doctor.gender = gender
        if date_of_birth:
                doctor.date_of_birth = date_of_birth
        self._save_data()
        return True, "Personal information added successfully"

    def update_doctor_details(self,username,new_password,new_name,new_gender,new_address,new_email, new_contact_num,new_department,new_speciality):
        doctor=next((d for d in self.doctors if d.username==username),None)
        if doctor is None:
            return False
        if new_password:
            doctor.password = new_password
        if new_name:
            doctor.name = new_name
        if new_gender:
            doctor.gender = new_gender
        if new_address:
            doctor.address = new_address
        if new_email:
            doctor.email = new_email
        if new_contact_num:
            doctor.contact_num = new_contact_num
        if new_speciality:
            doctor.speciality = new_speciality
        if new_department:
            doctor.department = new_department

        self._save_data()
        return True 
    
    def update_doctor_limited_info(self, username: str, new_contact_num: str | None = None, new_address: str | None = None):
        doc = self.get_doctor_by_username(username)
        if doc is None:
            return False, "Doctor not found"
        if not doc.update_contact(contact=new_contact_num, address=new_address):
            return False, "No fields to update"
        self._save_data()
        return True, "Updated successfully"
    
    def update_nurse_details(self, username, new_password=None, new_name=None, new_gender=None, new_address=None, new_email=None, new_contact_num=None, new_department=None, new_speciality=None):
        nurse = next((n for n in self.nurses if n.username == username), None)
        if nurse is None:
            return False
        if new_password: nurse.password = new_password
        if new_name: nurse.name = new_name
        if new_gender: nurse.gender = new_gender
        if new_address: nurse.address = new_address
        if new_email: nurse.email = new_email
        if new_contact_num: nurse.contact_num = new_contact_num
        if new_department: nurse.department = new_department
        if new_speciality: nurse.speciality = new_speciality
        self._save_data()
        return True

    # Admin - Add Patient
    def register_new_patient(self, username, password, name, gender, address, email, contact):
        from app.schedule import ScheduleManager
        from app.patient import PatientUser
        manager = ScheduleManager
        if not name or not password or not username or not gender or not address or not email or not contact:
            utils.log_event(f"Failed to register student: Details missing", "ERROR")
            return False, "Details required", None
        if "@" not in email:
            return False, "Invalid email address", None
        if any(r.email == email for r in manager.patients):
            return False, "Email already registered", None
        patient_id = f"S{manager.next_patient_id:04d}"
        date_joined = datetime.datetime.now().isoformat()
        patient = PatientUser(patient_id, username, password, name, gender, address, email, contact, date_joined)
        manager.patients.append(patient)
        manager.next_patient_id += 1
        manager.save()
        utils.log_event(f"Patient {name} registered with ID {patient_id}", "INFO")
        return True, f"Welcome {name}! Your ID is {patient_id}.", patient
    
    def register_new_doctor(self, username, password, name, gender, address, email, contact):
        from app.schedule import ScheduleManager
        from app.doctor import DoctorUser
        if not name or not password or not username or not gender or not address or not email or not contact:
            utils.log_event(f"Failed to register student: Details missing", "ERROR")
            return False, "Details required", None
        if "@" not in email:
            return False, "Invalid email address", None
        if any(r.email == email for r in ScheduleManager.doctors):
            return False, "Email already registered", None
        doctor_id = f"S{ScheduleManager.next_doctor_id:04d}"
        date_joined = datetime.datetime.now().isoformat()
        doctor = DoctorUser(doctor_id, username, password, name, gender, address, email, contact, date_joined)
        ScheduleManager.doctors.append(doctor)
        ScheduleManager.next_doctor_id += 1
        ScheduleManager.save()
        utils.log_event(f"Doctor {name} registered with ID {doctor_id}", "INFO")
        return True, f"Welcome {name}! Your ID is {doctor_id}.", doctor
    
    def register_new_nurse(self, username, password, name, gender, address, email, contact):
        from app.schedule import ScheduleManager
        from app.nurse import NurseUser
        if not name or not password or not username or not gender or not address or not email or not contact:
            utils.log_event(f"Failed to register student: Details missing", "ERROR")
            return False, "Details required", None
        if "@" not in email:
            return False, "Invalid email address", None
        if any(r.email == email for r in ScheduleManager.nurses):
            return False, "Email already registered", None
        nurse_id = f"S{ScheduleManager.next_nurse_id:04d}"
        date_joined = datetime.datetime.now().isoformat()
        nurse = NurseUser(nurse_id, username, password, name, gender, address, email, contact, date_joined)
        ScheduleManager.nurses.append(nurse)
        ScheduleManager.next_nurse_id += 1
        ScheduleManager.save()
        utils.log_event(f"Nurse {name} registered with ID {nurse_id}", "INFO")
        return True, f"Welcome {name}! Your ID is {nurse_id}.", nurse

    def register_new_receptionist(self, username, password, name, gender, address, email, contact):
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
    
    def update_profile(self, **kwargs):
        """Allow partial updates to user details"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# TODO: encrypt password
# TODO:  self.date_joined = str(date_joined)