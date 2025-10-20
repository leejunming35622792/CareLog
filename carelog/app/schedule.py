import json, os

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
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Patient objects
            self.patients = [PatientUser(p["p_id"], p["username"], p["password"], p["name"], p["bday"], p["gender"], p["address"], p["email"], p["contact_num"], p["date_joined"], p["p_record"], p["p_remark"]) for p in data.get("patients", [])]

            # Doctor objects
            self.doctors = [DoctorUser(d["d_id"], d["username"], d["password"], d["name"], d["bday"], d["gender"], d["address"], d["email"], d["contact_num"], d["date_joined"], d["speciality"], d["department"]) for d in data.get("doctors", [])]

            # Nurse objects
            self.nurses = [NurseUser(n["n_id"], n["username"], n["password"], n["name"], n["bday"], n["gender"], n["address"], n["email"], n["contact_num"], n["date_joined"], n["speciality"], n["department"], n["with_doctor"]) for n in data.get("nurses", [])]

            # Receptionist objects
            self.receptionists = [ReceptionistUser(r["r_id"], r["username"], r["password"], r["name"], r["bday"], r["gender"], r["address"], r["email"], r["contact_num"], r["date_joined"]) for r in data.get("receptionists", [])]

            # Admin objects
            self.admins = [AdminUser(a["a_id"], a["username"], a["password"], a["name"], a["bday"], a["gender"], a["address"], a["email"], a["contact_num"], a["date_joined"]) for a in data.get("admins", [])]

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

        # if file doesn't exist
        if not os.path.exists(self.data_path):
            utils.log_event("Data file not found. Creating default data file.", "WARNING")
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2)
            return default_data

        # if file exists
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

                # if file is empty
                if not content:
                    utils.log_event("Data file empty. Resetting to default data.", "WARNING")
                    with open(self.data_path, "w", encoding="utf-8") as f2:
                        json.dump(default_data, f2, indent=2)
                    return default_data

                # if file has valid JSON
                data = json.loads(content)
                return data

        except json.JSONDecodeError:
            utils.log_event("Data file invalid JSON. Resetting to default data.", "ERROR")
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2)
            return default_data


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

    def add_user(self, role, user_obj):
        """Add a new user to the correct list and increment ID"""
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
        else:
            raise ValueError(f"Invalid role: {role}")

        self.save()
        return True

    # Additional
    def get_patient_count(self):
        return len(self.patients)

    def get_doctor_count(self):
        return len(self.doctors)

    # Helper functions
    def find_doctor_by_id(self,doctor_id):
        doctor = next((d for d in self.doctors if d.d_id == doctor_id),None)
        if doctor is None:
            return False, "No doctor found",None
        return doctor
    
    def find_nurse_by_id(self,nurse_id):
        nurse = next((n for n in self.nurses if n.n_id == nurse_id),None)
        if nurse is None:
            return False,"No nurse found",None
        return nurse
    
    def find_patient_by_id(self,patient_id):
        patient = next((p for p in self.patients if p.p_id == patient_id),None)
        if patient is None:
            return False,"No patient found",None
        return patient
    
    def find_remark_by_id(self,remark_id):
        remark = next((r for r in self.remarks if r.remark_id == remark_id),None)
        if remark is None:
            return False, "No remark found", None
        return remark

    def find_appointment_by_id(self,appointment_id):
        appt = next((a for a in self.appointments if a.appt_id == appointment_id),None)
        if appt is None:
            return False, "No appointment found", None
        return appt
    
    #view patient details for nurse
    def view_patient_details_by_nurse(self, patient_id):
        "View patient details"
        patient = self.find_patient_by_id(patient_id)
        if not patient:
            return False, "Patient not found", None
        patient_records = [r for r in self.records if r.p_id == patient_id]
        patient_remarks = [r for r in self.remarks if r.patient_id == patient_id and r.is_active]
        
        patient_info = {
            "patient_id": patient.p_id,
            "name": patient.name,
            "gender": patient.gender,
            "email": patient.email,
            "contact": patient.contact_num,
            "address": patient.address,
            "records_count": len(patient_records),
            "remark_count": len(patient_remarks),
            "records": [
                {
                    "record_id": r.pr_record_id,
                    "timestamp": r.pr_timestamp,
                    "conditions": r.pr_conditions,
                    "medications": r.pr_medications,
                    "remark": r.pr_remark
                } for r in patient_records
            ],
            "remarks": [
                {
                    "remark_id": r.remark_id,
                    "doctor_id": r.doctor_id,
                    "timestamp": r.timestamp,
                    "type": r.remark_type,
                    "content": r.content
                } for r in patient_remarks
            ]
        }
        utils.log_event(f"Nurse viewed patient {patient_id} details", "INFO")
        return True, "Patient details retrieved successfully", patient_info
    
    def add_patient_remark_nurse(self, patient_id, nurse_username, remark_type, content):
        """Add remark to patient (Nurse perspective)"""
        import datetime
        
        # Find nurse by username
        nurse = next((n for n in self.nurses if n.username == nurse_username), None)
        if not nurse:
            return False, "Nurse not found", None
        
        # Validate the patient
        patient = self.find_patient_by_id(patient_id)
        if not patient:
            return False, "Patient not found", None
        
        # Get doctor the nurse is working with
        doctor_id = nurse.with_doctor
        
        remark_id = self.next_remark_id
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_remark = PatientRemark(
            remark_id=remark_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            timestamp=timestamp,
            remark_type=remark_type,
            content=f"[Nurse {nurse.name}] {content}",
            is_active=True
        )
        
        self.remarks.append(new_remark)
        self.next_remark_id += 1
        self.save()
        
        utils.log_event(f"Nurse {nurse_username} added remark {remark_id} for patient {patient_id}", "INFO")
        return True, "Remark added successfully", remark_id

    def view_patient_remarks_nurse(self, patient_id):
        """View all remarks for a patient"""
        patient = self.find_patient_by_id(patient_id)
        if not patient:
            return False, "Patient not found", None
        
        remarks = [r for r in self.remarks if r.patient_id == patient_id and r.is_active]
        
        if not remarks:
            return False, f"No remarks found for patient {patient_id}", None
        
        results = [
            {
                "remark_id": r.remark_id,
                "doctor_id": r.doctor_id,
                "timestamp": r.timestamp,
                "type": r.remark_type,
                "content": r.content,
                "last_modified": r.last_modified
            } for r in remarks
        ]
        
        return True, f"Found {len(results)} remark(s)", results

    def update_patient_remark_nurse(self, remark_id, new_content):
        """Update a remark"""
        remark = self.find_remark_by_id(remark_id)
        if not remark:
            return False, "Remark not found", None
        
        remark.update_content(new_content)
        self.save()
        
        utils.log_event(f"Nurse updated remark {remark_id}", "INFO")
        return True, "Remark updated successfully", remark_id

    def delete_patient_remark_nurse(self, remark_id):
        """Soft delete a remark"""
        remark = self.find_remark_by_id(remark_id)
        if not remark:
            return False, "Remark not found", None
        
        remark.deactivate()
        self.save()
        
        utils.log_event(f"Nurse deleted remark {remark_id}", "INFO")
        return True, "Remark deleted successfully", remark_id

    def search_appointments_by_date(self, date):
        """Search appointments by date"""
        appts = [a for a in self.appointments if a.date == date]
        
        if not appts:
            return False, f"No appointments found for {date}", None
        
        results = [
            {
                "appt_id": a.appt_id,
                "patient_id": a.p_id,
                "doctor_id": a.d_id,
                "time": a.time,
                "status": a.status
            } for a in appts
        ]
        
        return True, f"Found {len(results)} appointment(s)", results

    def get_todays_appointments(self):
        """Get today's appointments"""
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return self.search_appointments_by_date(today)