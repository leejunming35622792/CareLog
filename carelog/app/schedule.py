import json
import datetime
import os

from app.user import User
from app.patient import PatientUser
from app.patient import PatientRecord
from app.patient import PatientAppointment
from app.doctor import DoctorUser
from app.nurse import NurseUser
from app.receptionist import ReceptionistUser
from app.admin import AdminUser
from app.shift_schedule import Shift

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
        self.next_patient_id = 1
        self.next_doctor_id = 1
        self.next_nurse_id = 1
        self.next_receptionist_id = 1
        self.next_admin_id = 1
        self.next_record_id = 1
        self.next_appt_id = 1
        self.next_shift_id = 1

        # Load existing data
        self._load_data()

    # Read existing data in the database, otherwise set to default value if it's empty
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

                # Patient record objects
                self.records = [PatientRecord(pr["pr_record_id"], pr["p_id"], pr["pr_timestamp"], pr["pr_conditions"], pr["pr_medications"], pr["pr_billings"], pr["pr_prediction_result"], pr["pr_confidence_score"]) for pr in data.get("records", [])]

                self.appointments = [PatientAppointment(appt["appt_id"], appt["patient"], appt["doctor"], appt["date"], appt["time"], appt["appt_status"], appt["appt_remark"]) for appt in self.appointments]

                # Shift objects
                self.shifts = [Shift(s["shift_id"], s["staff_id"], s["day"], s["start_time"], s["end_time"], s["remark"]) for s in data.get("shifts", [])]

                self.next_patient_id = data.get("next_patient_id", 1)
                self.next_doctor_id = data.get("next_doctor_id", 1)
                self.next_nurse_id = data.get("next_nurse_id", 1)
                self.next_receptionist_id = data.get("next_receptionist_id", 1)
                self.next_admin_id = data.get("next_admin_id", 1)
                self.next_record_id = data.get("next_record_id", 1)
                self.next_appt_id = data.get("next_appt_id", 1)
                self.next_shift_id = data.get("next_shift_id", 1)
        
        except FileNotFoundError:
            print("Data file not found, Starting with a clean state.")

    def _save_data(self):
        data_to_save = {
            "patients": [p.__dict__ for p in self.patients],
            "doctors": [d.__dict__ for d in self.doctors],
            "nurses": [n.__dict__ for n in self.nurses],
            "receptionists": [r.__dict__ for r in self.receptionists],
            "admins": [a.__dict__ for a in self.admins],
            "records": [pr.__dict__ for pr in self.records],
            "shifts": [s.__dict__ for s in self.shifts],
            "next_patient_id": self.next_patient_id,
            "next_doctor_id": self.next_doctor_id,
            "next_nurse_id": self.next_nurse_id,
            "next_receptionist_id": self.next_receptionist_id,
            "next_admin_id": self.next_admin_id,
            "next_record_id": self.next_record_id,
            "next_appt_id": self.next_appt_id,
            "next_shift_id": self.next_shift_id
        }
        with open(self.data_path, "w") as f:
            json.dump(data_to_save, f, indent=4)

    def save(self):
        self._save_data()

    def add_account_patient(self, username, password):
        joined_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_patient = PatientUser(self.next_patient_id, 
                                username,
                                password, 
                                "", #name
                                "", #gender
                                "", #address
                                "", #email
                                "", #contact_unum
                                joined_date, #date_joined
                                [])
        self.patients.append(new_patient)
        self.next_patient_id += 1
        return True
    
    def update_patient_detail(self, username, new_password, new_name, new_gender, new_address, new_email, new_contact_num, new_remark):
        patient = next((p for p in self.patients if p.username == username), None)
        
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
        
        return True