import json, datetime, os

from app.user import User
from app.patient import PatientUser
from app.patient import PatientRecord
from app.patient import PatientAppointment
from app.doctor import DoctorUser
from app.nurse import NurseUser
from app.receptionist import ReceptionistUser
from app.admin import AdminUser
from app.shift_schedule import Shift
from app.remark import PatientRemark
import app.utils as utils

class ScheduleManager():
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.patients = []
        self.doctors = []
        self.nurses = []
        self.receptionists = []
        self.admins = []
        self.records = []
        self.appointments = []
        self.shifts = []
        self.remarks=[]
        self.next_patient_id = 1
        self.next_doctor_id = 1
        self.next_nurse_id = 1
        self.next_receptionist_id = 1
        self.next_admin_id = 1
        self.next_record_id = 1
        self.next_appt_id = 1
        self.next_shift_id = 1
        self.next_remark_id=1
        self.systemlogs = []

        # Load existing data
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)

                # Patient objects
                self.patients = [PatientUser(p["p_id"], p["username"], p["password"], p["name"], p["gender"], p["address"], p["email"], p["contact_num"], p["date_joined"], p["p_record"], p["p_remark"]) for p in data.get("patients", [])]

                # Doctor objects
                self.doctors = [DoctorUser(d["d_id"], d["username"], d["password"], d["name"], d["gender"], d["address"], d["email"], d["contact_num"], d["date_joined"], d["speciality"], d["department"]) for d in data.get("doctors", [])]

                # Nurse objects
                self.nurses = [NurseUser(n["n_id"], n["username"], n["password"], n["name"], n["gender"], n["address"], n["email"], n["contact_num"], n["date_joined"], n["speciality"], n["department"], n["with_doctor"]) for n in data.get("nurses", [])]

                # Receptionist objects
                self.receptionists = [ReceptionistUser(r["r_id"], r["username"], r["password"], r["name"], r["gender"], r["address"], r["email"], r["contact_num"], r["date_joined"]) for r in data.get("receptionists", [])]

                # Admin objects
                self.admins = [AdminUser(a["a_id"], a["username"], a["password"], a["name"], a["gender"], a["address"], a["email"], a["contact_num"], a["date_joined"]) for a in data.get("admins", [])]

                # Patient records
                self.records = [PatientRecord(pr["pr_record_id"], pr["p_id"], pr["pr_timestamp"], pr["pr_conditions"], pr["pr_medications"], pr["pr_billings"], pr["pr_prediction_result"], pr["pr_confidence_score"], pr["pr_remark"]) for pr in data.get("records", [])]

                # Patient appointments
                self.appointments = [PatientAppointment(appt["appt_id"], appt["p_id"], appt["d_id"], appt["date"], appt["time"], appt["status"], appt["remark"]) for appt in data.get("appointments", [])]

                # Shift objects
                self.shifts = [Shift(s["shift_id"], s["staff_id"], s["day"], s["start_time"], s["end_time"], s["remark"]) for s in data.get("shifts", [])]

                # Patient Remark Objects
                self.remarks = [PatientRemark(rm["remark_id"], rm["patient_id"], rm["doctor_id"], rm["timestamp"], rm["remark_type"], rm["content"], rm["is_active"]) for rm in data.get("remarks", [])]
                # TODO: self.remarks= [PatientRemark.from_dict(rm) for rm in data.get("remarks",[])]

                self.next_patient_id = data.get("next_patient_id", 1)
                self.next_doctor_id = data.get("next_doctor_id", 1)
                self.next_nurse_id = data.get("next_nurse_id", 1)
                self.next_receptionist_id = data.get("next_receptionist_id", 1)
                self.next_admin_id = data.get("next_admin_id", 1)
                self.next_record_id = data.get("next_record_id", 1)
                self.next_appt_id = data.get("next_appt_id", 1)
                self.next_shift_id = data.get("next_shift_id", 1)
                self.next_remark_id=data.get("next_remark_id",1)
                return data
        
        except FileNotFoundError:
            utils.log_event("Data file not found, Starting with a clean state.", "WARNING")
            return {}

    def _save_data(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        data_to_save = {
            "patients": [p.__dict__ for p in self.patients],
            "doctors": [d.__dict__ for d in self.doctors],
            "nurses": [n.__dict__ for n in self.nurses],
            "receptionists": [r.__dict__ for r in self.receptionists],
            "admins": [a.__dict__ for a in self.admins],
            "records": [pr.__dict__ for pr in self.records],
            "appointments": [a.__dict__ for a in self.appointments],
            "shifts": [s.__dict__ for s in self.shifts],
            "remarks":[r.__dict__ for r in self.remarks],
            "next_patient_id": self.next_patient_id,
            "next_doctor_id": self.next_doctor_id,
            "next_nurse_id": self.next_nurse_id,
            "next_receptionist_id": self.next_receptionist_id,
            "next_admin_id": self.next_admin_id,
            "next_record_id": self.next_record_id,
            "next_appt_id": self.next_appt_id,
            "next_shift_id": self.next_shift_id,
            "next_remark_id": self.next_remark_id
        }
        try:
            with open(self.data_path, "w") as f:
                json.dump(data_to_save, f, indent=4)
        except OSError as e:
            utils.log_event(f"Error saving data: {e}", "ERROR")
            raise
            
    def save(self): 
        self._save_data()

    # Additional
    def get_patient_count(self):
        return len(self.patients)

    def get_doctor_count(self):
        return len(self.doctors)

    # --- Login ---
    def check_credentials(self, staff, username, password):
        # Map each role to its user-password dict
        accounts = {
            "Patient": {p.username: p.password for p in self.patients},
            "Doctor": {d.username: d.password for d in self.doctors},
            "Nurse": {n.username: n.password for n in self.nurses},
            "Receptionist": {r.username: r.password for r in self.receptionists},
            "Admin": {a.username: a.password for a in self.admins},
        }

        # Check if role exists
        if staff not in accounts:
            return False

        acc = accounts[staff]

        # Verify username and password
        if username in acc and acc[username].strip() == password:
            return staff
        else:
            return False

    def create_account(self, role, user_obj):
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
        self.save()

    def login_doctor(self,username,password):
        doctor=next((d for d in self.doctors if d.username==username))
        if doctor is None:
            return False, "Doctor Not Found ", None
        if doctor.password != password:
            return False, "Incorrect Password"
        
        return True, "Logic Successful", doctor

    # --- Patients ---
    def search_record(self, p_id, record_id):
        record_dict = {}
        for record in self.records:
            if record_id == record.pr_record_id:
                record_dict = {
                    "Record ID": record.pr_record_id,
                    "Patient ID": record.p_id,
                    "Date": record.pr_timestamp,
                    "Conditions": ", ".join(record.pr_conditions.keys()),
                    # "Conditions": ", ".join([f"{condition}: {severity}" for condition, severity in record.pr_conditions.items()]),
                    "Medications": record.pr_medications,
                    "Billings": record.pr_billings,
                    "Prediction Result": record.pr_prediction_result,
                    "Confidence Score": record.pr_confidence_score,
                    "Remark": record.pr_remark,
                }
        return record_dict

    def search_appt(self, chosen_appt_id):
        for appt in self.appointments:
            if appt.appt_id == chosen_appt_id:
                return {
                    "Appointment ID": appt.appt_id,
                    "Patient ID": appt.p_id,
                    "Doctor ID": appt.d_id,
                    "Appointment Date": appt.date,
                    "Appointment Time": appt.time,
                    "Appointment Status": appt.status,
                    "Remark": appt.remark
                }

    # --- Doctors ---
    def view_doctor_details(self,username):
        doctor = next((d for d in self.doctors if d.username == username), None)

        if doctor is None:
            return None, "Doctor Not Found"
        
        # if doctor.password != password:
        #     return False, "Doctor Not Found", None
        
        profile= {
            "staff_id":doctor.d_id,
            "name":doctor.name,
            "email":doctor.email,
            "contact_num": doctor.contact_num,
            "address": doctor.address,
            "gender": doctor.gender,
            "date_of_birth": getattr(doctor,"date_of_birth",""),
            "department": doctor.department,
            "speciality": doctor.speciality,
            "date_joined": doctor.date_joined,
        }
        return profile, "Profile Successfully Retrieved"
    
    def view_patient_details_by_doctor(self,patient_id :int):
        patient=next((p for p in self.patients if p.p_id ==patient_id),None)
        if patient is None:
            return False,"Patient Not Found", None
        patient_records=[r for r in self.records if r.patient==patient_id]
        previous_conditions: list[str]=[]
        medication_history: list[str]=[]
        for record in patient_records:
            if getattr(record,"pr_conditions",None):
                previous_conditions.extend(record.pr_conditions)
            if hasattr(record,"pr_medications") and record.pr_medications:
                medication_history.extend(record.pr_medications)
        previous_conditions = list(set(previous_conditions))
        info = {
            "patient_id": patient.p_id,
            "name": patient.name,
            "gender": patient.gender,
            "date_of_birth": getattr(patient, "date_of_birth", ""),
            "previous_conditions": previous_conditions,
            "medication_history": medication_history,
            }
        return True, "Patient details retrieved successfully", info

    def view_patient_remarks(self, patient_id: int, remark_type: str | None = None, limit: int | None = None):
        patient = self.get_patient_by_id(patient_id)
        if patient is None:
            return False, "Patient not found", []
        items = [rm for rm in self.remarks if rm.patient_id == patient_id and rm.is_active]
        if remark_type:
            items = [rm for rm in items if rm.remark_type == remark_type]
        items.sort(key=lambda x: x.timestamp, reverse=True)
        if limit:
            items = items[:limit]
        out = []
        for rm in items:
            doc = self.get_doctor_by_id(rm.doctor_id)
            out.append(
                {
                    "remark_id": rm.remark_id,
                    "doctor_id": rm.doctor_id,
                    "doctor_name": (doc.name if doc else "Unknown Doctor"),
                    "timestamp": rm.timestamp,
                    "remark_type": rm.remark_type,
                    "content": rm.content,
                    "last_modified": rm.last_modified,
                }
            )
        return True, f"Found {len(out)} remarks", out

    def add_patient_remark(self,patient_id :int , doctor_username: str, remark_type: str, remark_content :str):
        patient=next((p for p in self.patients if p.p_id==patient_id), None)
        if patient is None:
            return False, "Patient Not Found", None
        doctor=next((d for d in self.doctors if d.username == doctor_username), None)
        if doctor is None:
            return False, "Doctor Not Found", None
        valid_types=["mood", "pain_level"," dietary","general","observation"]
        r_type=remark_type.strip().lower()
        if r_type not in valid_types:
            return False, f" Invalid Remark Type. Must be one of : {', '.join (valid_types)}", None
        remark_id = f"RM{self.next_remark_id:04d}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_remark=PatientRemark(
            remark_id=remark_id,
            patient_id=patient_id,
            doctor_id=doctor.d_id,
            timestamp=timestamp,
            remark_type=r_type,
            content=remark_content,
            is_active=True
        )
        self.remarks.append(new_remark)
        rid=self.next_remark_id
        self.next_remark_id+=1
        self._save_data()
        return True, "Remark added successfully", rid

    def edit_patient_remark(self, remark_id: int, doctor_username: str, new_content: str):
        remark = next((rm for rm in self.remarks if rm.remark_id == remark_id), None)
        if remark is None:
            return False, "Remark not found"
        doc = self.get_doctor_by_username(doctor_username)
        if doc is None:
            return False, "Doctor not found"
        if remark.doctor_id != doc.d_id:
            return False, "You can only edit your own remarks"
        remark.update_content(new_content)
        self._save_data()
        return True, "Remark updated successfully"

    def get_remarks_by_type(self, patient_id: int, remark_type: str):
        return self.view_patient_remarks(patient_id, remark_type=remark_type)
    
    def get_recent_patient_remarks(self, patient_id: int, days: int = 7):
        patient = self.get_patient_by_id(patient_id)
        if patient is None:
            return False, "Patient not found", []
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        recent = []
        for rm in self.remarks:
            if rm.patient_id == patient_id and rm.is_active:
                try:
                    dt = datetime.datetime.strptime(rm.timestamp, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if dt >= cutoff:
                    doc = self.get_doctor_by_id(rm.doctor_id)
                    recent.append(
                        {
                            "remark_id": rm.remark_id,
                            "doctor_name": (doc.name if doc else "Unknown"),
                            "timestamp": rm.timestamp,
                            "remark_type": rm.remark_type,
                            "content": rm.content,
                        }
                    )
        recent.sort(key=lambda x: x["timestamp"], reverse=True)
        return True, f"Found {len(recent)} remarks from last {days} days ", recent

    # --- Appointments ---
    def add_appointments(self, p_id, d_id, appt_date, appt_time, appt_remark):
        appt_id = f"AAPT{self.next_appt_id:04d}"
        new_appt = PatientAppointment.create(appt_id, p_id, d_id, appt_date, appt_time, "Pending", appt_remark)
        self.appointments.append(new_appt)
        self.next_appt_id += 1
        self._save_data()
        return True

    def view_upcoming_appointments(self,username):
        doctor=next((d for d in self.doctors if d.username ==username), None)
        if doctor is None:
            return False, "No Doctor Found", None
        now = datetime.datetime.now()
        upcoming: list[dict]=[]

        for appt in self.appointments:
            if appt.doctor==doctor.d_id:
                try:
                    appt_dt=datetime.datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
                    if appt_dt >= now:
                        patient = self.get_patient_by_id(appt.patient)
                        upcoming.append(
                            {
                            "appt_id": appt.appt_id,
                            "patient_id": appt.patient,
                            "patient_name": patient.name if patient else "Unknown",
                            "date": appt.date,
                            "time": appt.time,
                            "status": appt.appt_status,
                            "remark": appt.appt_remark,
                            }
                        )
                except ValueError:
                    continue
        upcoming.sort(key=lambda x: f"{x['date']} {x['time']}")
        return True, f"Found {len(upcoming)} upcoming appointments", upcoming
    
    def edit_appointments(self, appt_id, d_id, appt_date, appt_time, appt_remark):
        for appt in self.appointments:
            if appt.appt_id == appt_id:
                if d_id:
                    appt.d_id = d_id
                if appt_date:
                    appt.date = appt_date
                if appt_time:
                    appt.time = appt_time
                if appt_remark:
                    appt.remark = appt_remark
            return True

    def delete_appointments(self, appt_id):
        self.appointments = [appt for appt in self.appointments if appt.appt_id != appt_id]
        return True

    # --- Nurse ---
    def view_nurse_details(self, username, password):
        nurse = next((n for n in self.nurses if n.username == username), None)
        if nurse is None:
            return False, "Nurse not found", None
        if nurse.password != password:
            return False, "Incorrect password", None
        
        profile = {
            "staff_id": nurse.n_id,
            "name": nurse.name,
            "email": nurse.email,
            "contact_num": nurse.contact_num,
            "address": nurse.address,
            "gender": nurse.gender,
            "date_of_birth": getattr(nurse, "date_of_birth", ""),
            "department": nurse.department,
            "speciality": nurse.speciality,
            "date_joined": nurse.date_joined,
            "with_doctor": nurse.with_doctor
        }
        return True, "Profile successfully retrieved", profile
    
    def view_patient_details_by_nurse(self, patient_id: int):
        patient = next((p for p in self.patients if p.p_id == patient_id), None)
        if patient is None:
            return False, "Patient not found", None
        info = {
            "patient_id": patient.p_id,
            "name": patient.name,
            "gender": patient.gender,
            "date_of_birth": getattr(patient, "date_of_birth", ""),
            "remarks": getattr(patient, "p_remark", [])
        }
        return True, "Patient details retrieved successfully", info
    
    def add_patient_remark_nurse(self, patient_id: int, nurse_username: str, remark_type: str, remark_content: str):
        patient = next ((p for p in self.patients if p.p_id == patient_id), None)
        if patient is None:
            return False, "Patient not found", None
        
        nurse = next ((n for n in self.nurses if n.username == nurse_username), None)
        if nurse is None:
            return False, "Nurse not found", None
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_remark = {
            "remark_id": self.next_remark_id,
            "nurse_id": nurse.n_id,
            "nurse_name": nurse.name,
            "timestamp": timestamp,
            "remark_type": remark_type,
            "content": remark_content
        }
        patient.p_remark.append(new_remark)
        self.next_remark_id += 1
        self._save_data()
        return True, "Remark added successfully", new_remark["remark_id"]
    
    #helper functions 
    def find_doctor_by_id(self,doctor_id):
        doctor=next((d for d in self.doctors if d.d_id == doctor_id),None)
        if doctor is None:
            return False, "No doctor found",None
        return doctor 
    
    def find_nurse_by_id(self,nurse_id):
        nurse=next((n for n in self.nurses if n.n_id == nurse_id),None)
        if nurse is None:
            return False,"No nurse found",None
        return nurse
    
    def find_patient_by_id(self,patient_id):
        patient=next((p for p in self.patients if p.p_id == patient_id),None)
        if patient is None:
            return False,"No patient found",None
        return patient
    
    def find_remark_by_id(self,remark_id):
        remark=next((r for r in self.remarks if r.remark_id ==remark_id),None)
        if remark is None:
            return False, "No remark found", None
        return remark

    def find_appointment_by_id(self,appointment_id):
        appt=next((a for a in self.add_appointments if a.appt_id == appointment_id),None)
        if appt is None:
            return False, "No appointment found", None
        return appt       