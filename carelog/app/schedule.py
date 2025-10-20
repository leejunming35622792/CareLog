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
import datetime

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
        except FileNotFoundError:
            utils.log_event("Data file not found, starting with a clean state.", "WARNING")
            data = {}
        except json.JSONDecodeError:
            utils.log_event("Data file invalid JSON, starting with a clean state.", "ERROR")
            data = {}

            return {
                "patients": [],
                "doctors": [],
                "nurses": [],
                "receptionists": [],
                "admins": [],
                "appointments": [],
                "remarks": []
            }

        self.patients = [
            PatientUser(
                p["p_id"], p["username"], p["password"], p["name"], p["bday"],
                p["gender"], p["address"], p["email"], p["contact_num"],
                p["date_joined"], p.get("p_record", []), p.get("p_remark", "")
            ) for p in data.get("patients", [])
        ]

        self.doctors = [
            DoctorUser(
                d["d_id"], d["username"], d["password"], d["name"], d["bday"],
                d["gender"], d["address"], d["email"], d["contact_num"],
                d["date_joined"], d["speciality"], d["department"]
            ) for d in data.get("doctors", [])
        ]

        self.nurses = [
            NurseUser(
                n["n_id"], n["username"], n["password"], n["name"], n["bday"],
                n["gender"], n["address"], n["email"], n["contact_num"],
                n["date_joined"], n["speciality"], n["department"], n["with_doctor"]
            ) for n in data.get("nurses", [])
        ]

        self.receptionists = [
            ReceptionistUser(
                r["r_id"], r["username"], r["password"], r["name"], r["bday"],
                r["gender"], r["address"], r["email"], r["contact_num"], r["date_joined"]
            ) for r in data.get("receptionists", [])
        ]

        self.admins = [
            AdminUser(
                a["a_id"], a["username"], a["password"], a["name"], a["bday"],
                a["gender"], a["address"], a["email"], a["contact_num"], a["date_joined"]
            ) for a in data.get("admins", [])
        ]

        self.appointments = [
            PatientAppointment(
                appt["appt_id"], 
                appt["p_id"], 
                appt["d_id"],
                appt["date"],          
                appt["time"],          
                appt["status"],        
                appt.get("remark", "") 
            ) for appt in data.get("appointments", [])
        ]


        self.remarks = [
            PatientRemark(
                remark_id   = r["remark_id"],
                patient_id  = r["patient_id"],
                doctor_id   = r["doctor_id"],
                timestamp   = r["timestamp"],
                remark_type = r["remark_type"],
                content     = r["content"],
                is_active   = r.get("is_active", True)
            ) for r in data.get("remarks", [])
        ]

        self.next_patient_id = data.get("next_patient_id", 1)
        self.next_doctor_id = data.get("next_doctor_id", 1)
        self.next_nurse_id = data.get("next_nurse_id", 1)
        self.next_receptionist_id = data.get("next_receptionist_id", 1)
        self.next_admin_id = data.get("next_admin_id", 1)
        self.next_record_id = data.get("next_record_id", 1)
        self.next_appt_id = data.get("next_appt_id", 1)
        self.next_shift_id = data.get("next_shift_id", 1)
        self.next_remark_id = data.get("next_remark_id", 1)
        return data


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
        return True, "Doctor Found", doctor
    
    def find_nurse_by_id(self,nurse_id):
        nurse = next((n for n in self.nurses if n.n_id == nurse_id),None)
        if nurse is None:
            return False,"No nurse found",None
        return True, "Nurse Found", nurse
    
    def find_patient_by_id(self,patient_id):
        patient = next((p for p in self.patients if p.p_id == patient_id),None)
        if patient is None:
            return False,"No patient found",None
        return True, "Patient Found", patient
    
    def find_remark_by_id(self,remark_id):
        remark = next((r for r in self.remarks if r.remark_id == remark_id),None)
        if remark is None:
            return False, "No remark found", None
        return True, "Remark found", remark

    def find_appointment_by_id(self,appointment_id):
        appt = next((a for a in self.appointments if a.appt_id == appointment_id),None)
        if appt is None:
            return False, "No appointment found", None
        return True, "Appointment found", appt

    def view_patient_details_by_nurse(self, patient_id):
        """View patient details including records and remarks"""
        found, msg, patient = self.find_patient_by_id(patient_id)
        
        if not found:
            return False, msg, None

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
            "remarks_count": len(patient_remarks),
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
        return True, "Patient details retrieved", patient_info

    def search_patient_by_name(self, name):
        """Search patients by name"""
        if not name or not name.strip():
            return False, "Please provide a name to search", None
        
        matching_patients = [
            p for p in self.patients 
            if name.lower() in p.name.lower()
        ]
        
        if not matching_patients:
            return False, f"No patients found with name containing '{name}'", None
        
        results = [
            {
                "patient_id": p.p_id,
                "name": p.name,
                "gender": p.gender,
                "contact": p.contact_num,
                "email": p.email
            } for p in matching_patients
        ]
        
        utils.log_event(f"Nurse searched for patients with name '{name}'", "INFO")
        return True, f"Found {len(results)} patient(s)", results

    def create_appointment_nurse(self, patient_id, doctor_id, date, time, remark):
        """Create a new appointment"""
        found_p, msg_p, patient = self.find_patient_by_id(patient_id)
        if not found_p:
            return False, msg_p, None

        found_d, msg_d, doctor = self.find_doctor_by_id(doctor_id)
        if not found_d:
            return False, msg_d, None

        appt_id = f"A{self.next_appt_id:04d}"

        new_appointment = PatientAppointment(
            appt_id=appt_id,
            p_id=patient_id,
            d_id=doctor_id,
            appt_date=date,
            appt_time=time,
            appt_status="scheduled",
            appt_remark=remark
        )

        self.appointments.append(new_appointment)
        self.next_appt_id += 1

        utils.log_event(f"Appointment created: {appt_id}", "INFO")
        self.save()

        return True, f"Appointment {appt_id} created successfully", new_appointment


    def view_appointment_nurse(self, appointment_id=None, patient_id=None):
        """View appointments - all, by ID, or by patient"""
        if appointment_id:
            found, msg, appt = self.find_appointment_by_id(appointment_id)
            if not found:
                return False, msg, None

            
            return True, "Appointment found", {
                "appt_id": appt.appt_id,
                "patient_id": appt.p_id,
                "doctor_id": appt.d_id,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "remark": appt.remark
            }

        elif patient_id:
            appts = [a for a in self.appointments if a.p_id == patient_id]
            if not appts:
                return False, f"No appointments found for patient {patient_id}", None
            
            results = [
                {
                    "appt_id": a.appt_id,
                    "doctor_id": a.d_id,
                    "date": a.date,
                    "time": a.time,
                    "status": a.status,
                    "remark": a.remark
                } for a in appts
            ]
            return True, f"Found {len(results)} appointment(s)", results
        
        else:
            results = [
                {
                    "appt_id": a.appt_id,
                    "patient_id": a.p_id,
                    "doctor_id": a.d_id,
                    "date": a.date,
                    "time": a.time,
                    "status": a.status
                } for a in self.appointments
            ]
            return True, f"Found {len(results)} appointment(s)", results

    def update_appointment_nurse(self, appt_id, date=None, time=None, status=None, remark=None):
        """Update appointment details"""
        found, msg, appt = self.find_appointment_by_id(appt_id)
        if not found:
            return False, msg, None

        if date:
            appt.date = date
        if time:
            appt.time = time
        if status:
            if status not in ["scheduled", "completed", "cancelled", "no-show"]:
                return False, "Invalid status", None
            appt.status = status
        if remark is not None:
            appt.remark = remark

        utils.log_event(f"Appointment updated: {appt_id}", "INFO")
        self.save()

        return True, f"Appointment {appt_id} updated successfully", appt


    def delete_appointment_nurse(self, appointment_id):
        """Cancel/delete appointment"""
        found, msg, appt = self.find_appointment_by_id(appointment_id)
        if not found:
            return False, msg, None

        
        appt.status = "cancelled"
        self.save()
        
        utils.log_event(f"Nurse cancelled appointment {appointment_id}", "INFO")
        return True, "Appointment cancelled successfully", appointment_id

    def create_patient_record_nurse(self, patient_id, conditions, medications, remark=""):
        """Create new patient record"""
        import datetime
        
        found, msg, patient = self.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None


        
        record_id = f"PR{self.next_record_id:04d}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_record = PatientRecord(
            pr_record_id=record_id,
            p_id=patient_id,
            pr_timestamp=timestamp,
            pr_conditions=conditions,
            pr_medications=medications,
            pr_billings="",
            pr_prediction_result="",
            pr_confidence_score=0.0,
            pr_remark=remark
        )
        
        self.records.append(new_record)
        self.next_record_id += 1
        self.save()
        
        utils.log_event(f"Nurse created record {record_id} for patient {patient_id}", "INFO")
        return True, "Patient record created successfully", record_id

    def view_patient_records_nurse(self, patient_id):
        """View all records for a patient"""
        found, msg, patient = self.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None

        
        records = [r for r in self.records if r.p_id == patient_id]
        
        if not records:
            return False, f"No records found for patient {patient_id}", None
        
        results = [
            {
                "record_id": r.pr_record_id,
                "timestamp": r.pr_timestamp,
                "conditions": r.pr_conditions,
                "medications": r.pr_medications,
                "remark": r.pr_remark
            } for r in records
        ]
        
        return True, f"Found {len(results)} record(s)", results

    def update_patient_record_nurse(self, record_id, conditions=None, medications=None, remark=None):
        """Update patient record (conditions and medications only)"""
        record = next((r for r in self.records if r.pr_record_id == record_id), None)
        if not record:
            return False, "Record not found", None
        
        if conditions is not None:
            record.pr_conditions = conditions
        if medications is not None:
            record.pr_medications = medications
        if remark is not None:
            record.pr_remark = remark
        
        self.save()
        utils.log_event(f"Nurse updated record {record_id}", "INFO")
        return True, "Record updated successfully", record_id

    def delete_patient_record_nurse(self, record_id):
        """Delete patient record"""
        record = next((r for r in self.records if r.pr_record_id == record_id), None)
        if not record:
            return False, "Record not found", None
        
        self.records.remove(record)
        self.save()
        
        utils.log_event(f"Nurse deleted record {record_id}", "INFO")
        return True, "Record deleted successfully", record_id

    def add_patient_remark_nurse(self, patient_id, nurse_username, remark_type, content):
        """Add remark to patient (Nurse perspective)"""
        import datetime
        
        nurse = next((n for n in self.nurses if n.username == nurse_username), None)
        if not nurse:
            return False, "Nurse not found", None
        
        found, msg, patient = self.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None

        
        doctor_id = nurse.with_doctor
        
        remark_id = self.next_remark_id
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_remark = PatientRemark(
            remark_id   = str(remark_id),
            patient_id  = patient_id,
            doctor_id   = doctor_id,
            timestamp   = timestamp,
            remark_type = remark_type,
            content     = f"[Nurse {nurse.name}] {content}",
            is_active   = True
        )
        
        self.remarks.append(new_remark)
        self.next_remark_id += 1
        self.save()
        
        utils.log_event(f"Nurse {nurse_username} added remark {remark_id} for patient {patient_id}", "INFO")
        return True, "Remark added successfully", remark_id

    def view_patient_remarks_nurse(self, patient_id):
        """View all remarks for a patient"""
        found, msg, patient = self.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None

        
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
        found, msg, remark = self.find_remark_by_id(remark_id)
        if not found:
            return False, msg, None

        
        remark.update_content(new_content)
        self.save()
        
        utils.log_event(f"Nurse updated remark {remark_id}", "INFO")
        return True, "Remark updated successfully", remark_id

    def delete_patient_remark_nurse(self, remark_id):
        """Soft delete a remark"""
        found, msg, remark = self.find_remark_by_id(remark_id)
        if not found:
            return False, msg, None

        
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