import datetime
from app.user import User
import app.utils as utils
import helper_manager.record_manager as hm

class NurseUser(User):
    def __init__(self, n_id, username, password, name, bday, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        self.n_id = n_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)
        self.speciality = speciality
        self.department = department 
        self.with_doctor = with_doctor  # store doctor ID

    def create_patient_record(self, patient_id, conditions, medications, remark=""):
        """Create new patient record"""
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        found, msg, patient = sc.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None
        
        record_id = f"PR{sc.next_record_id:04d}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_record = hm.create_patient_record_nurse(record_id, patient_id, timestamp, conditions, medications, remark)

        sc.records.append(new_record)
        sc.next_record_id += 1
        sc.save()

        utils.log_event(f"Nurse created record {record_id} for patient {patient_id}", "INFO")
        return True, "Patient record created successfully", record_id
    
    def view_patient_records(self, patient_id):
        """View all records for a patient"""
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        found, msg, patient = sc.find_patient_by_id(patient_id)
        if not found:
            return False, msg, None
        
        records = [r for r in sc.records if r.p_id == patient_id]
        if not records:
            return False, f"No records found for patient {patient_id}", None
        
        record = hm.view_patient_records_nurse(records)

        return True, f"Found {len(record)} record(s)", record
    
    def update_patient_record(self, record_id, conditions, medications, remark):
        """Update patient record (conditions and medications only)"""
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        record = next((r for r in sc.records if r.pr_record_id == record_id), None)
        if not record:
            return False, "Record not found", None
        update = hm.update_patient_record_nurse(sc, record_id, conditions, medications, remark)
        if update:
            sc.save()
            utils.log_event(f"Nurse updated record {record_id}", "INFO")
            return True, "Record updated successfully", record_id
        return False, "Record update failed", record_id

    def delete_patient_record(self, record_id):
        """Delete patient record"""
        from app.schedule import ScheduleManager
        sc = ScheduleManager()
        record = next((r for r in sc.records if r.pr_record_id == record_id), None)
        if not record:
            return False, "Record not found", None
        
        sc.records.remove(record)
        sc.save()

        utils.log_event(f"Nurse deleted record {record_id}", "INFO")
        return True, "Record deleted successfully", record_id