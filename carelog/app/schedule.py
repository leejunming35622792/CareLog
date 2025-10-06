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
        appt = next((a for a in self.add_appointments if a.appt_id == appointment_id),None)
        if appt is None:
            return False, "No appointment found", None
        return appt