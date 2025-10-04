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
    def create_acc(id, username, password, date):
        return User(id, 
            username,
            password, 
            "", #name
            "", #gender
            "", #address
            "", #email
            "", #contact_num
            date, #date_joined
        )

    # Admin - Add Patient
    def register_new_patient(username, password, name, gender, address, email, contact):
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
    
    def register_new_doctor(username, password, name, gender, address, email, contact):
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
    
    def register_new_nurse(username, password, name, gender, address, email, contact):
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

# TODO: encrypt password
# TODO:  self.date_joined = str(date_joined)