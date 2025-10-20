from app.schedule import ScheduleManager
manager = ScheduleManager()
import app.utils as utils


def _persist():
    """Best-effort persistence without assuming exact method name/placement."""
    for obj, method in [
        (manager, "save_to_json"),
        (manager, "save"),
        (getattr(manager, "data_manager", None), "save_to_json"),
        (getattr(manager, "data_manager", None), "save"),
    ]:
        if obj and hasattr(obj, method):
            getattr(obj, method)()
            return

def search_record(p_id, record_id):
    """
    Search for a record by patient ID and record ID.

    Returns a display-friendly dict or {} if not found.
    """
    for record in manager.records:
        if record.pr_record_id == record_id and record.p_id == p_id:
            return {
                "Record ID": record.pr_record_id,
                "Patient ID": record.p_id,
                "Date": record.pr_timestamp,
                # Display: join keys; switch to the commented version to show severities
                "Conditions": ", ".join(getattr(record, "pr_conditions", {}).keys()),
                # "Conditions": ", ".join([f"{k}: {v}" for k, v in getattr(record, "pr_conditions", {}).items()]),
                "Medications": ", ".join(getattr(record, "pr_medications", [])),
                "Billings": getattr(record, "pr_billings", 0.0),
                "Prediction Result": getattr(record, "pr_prediction_result", None),
                "Confidence Score": getattr(record, "pr_confidence_score", None),
                "Remark": getattr(record, "pr_remark", ""),
            }
    return {}

def edit_record_doctor(p_id, record_id, **kwargs):
    """
    Edit an existing record by (p_id, record_id).

    Allowed kwargs:
        pr_conditions: dict[str, str]  e.g., {"Hypertension": "Moderate"}
        pr_medications: list[str]
        pr_billings: float|int
        pr_prediction_result: str
        pr_confidence_score: float (0..1 or 0..100 depending on your convention)
        pr_remark: str

    Returns:
        bool: True if updated (and persisted), False if not found or invalid.
    """
    for record in manager.records:
        if record.pr_record_id == record_id and record.p_id == p_id:

            # --- light validations (only when provided) ---
            if "pr_conditions" in kwargs:
                pc = kwargs["pr_conditions"]
                if not isinstance(pc, dict) or not all(isinstance(k, str) for k in pc.keys()):
                    print("Invalid pr_conditions: expected dict[str, str].")
                    return False
                record.pr_conditions = pc

            if "pr_medications" in kwargs:
                pm = kwargs["pr_medications"]
                if isinstance(pm, (list, tuple)) and all(isinstance(x, str) for x in pm):
                    record.pr_medications = list(pm)
                else:
                    print("Invalid pr_medications: expected list[str].")
                    return False

            if "pr_billings" in kwargs:
                try:
                    record.pr_billings = float(kwargs["pr_billings"])
                except (TypeError, ValueError):
                    print("Invalid pr_billings: expected a number.")
                    return False

            if "pr_prediction_result" in kwargs:
                record.pr_prediction_result = kwargs["pr_prediction_result"]

            if "pr_confidence_score" in kwargs:
                try:
                    score = float(kwargs["pr_confidence_score"])
                    record.pr_confidence_score = score
                except (TypeError, ValueError):
                    print("Invalid pr_confidence_score: expected a number.")
                    return False

            if "pr_remark" in kwargs:
                record.pr_remark = kwargs["pr_remark"]

            _persist()
            return True
    return False

def view_patient_records_doctor(self,patient_id):
    "View all records for a patient"
    patient=self.find_patient_by_id(patient_id)
    if not patient:
        return False,"Patient Not Found", None
    records=[r for r in self.records if r.p_id ==patient_id]

    if not records :
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

def view_patient_records_nurse(self, patient_id):
        """View all records for a patient"""
        patient = self.find_patient_by_id(patient_id)
        if not patient:
            return False, "Patient not found", None
        
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