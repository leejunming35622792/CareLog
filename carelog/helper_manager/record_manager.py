import os
import datetime
import app.utils as utils
#attempts to persist data using various possible save methods from ScheduleManager
def _persist():
    """Best-effort persistence without assuming exact method name/placement."""

    from app.schedule import ScheduleManager
    manager = ScheduleManager()

    for obj, method in [
        (manager, "save_to_json"),
        (manager, "save"),
        (getattr(manager, "data_manager", None), "save_to_json"),
        (getattr(manager, "data_manager", None), "save"),
    ]:
        if obj and hasattr(obj, method):
            getattr(obj, method)()
            return
#searches for a patient record by patient ID and record ID, returning a formatted dictionary
def search_record(p_id, record_id):
    """
    Search for a record by patient ID and record ID.
    Returns a display-friendly dict or {} if not found.
    """
    from app.schedule import ScheduleManager
    manager = ScheduleManager()
    for record in manager.records:
        if record.pr_record_id == record_id and record.p_id == p_id:
            return {
                "Record ID": record.pr_record_id,
                "Patient ID": record.p_id,
                "Date": record.pr_timestamp,
                # Display: join keys; switch to the commented version to show severities
                "Conditions": record.pr_conditions,
                # "Conditions": ", ".join(getattr(record, "pr_conditions", {}).keys()),
                "Medications": record.pr_medications,
                # "Medications": ", ".join(getattr(record, "pr_medications", [])),
                "Billings": getattr(record, "pr_billings", 0.0),
                "Prediction Result": getattr(record, "pr_prediction_result", None),
                "Confidence Score": getattr(record, "pr_confidence_score", None),
                "Remark": getattr(record, "pr_remark", ""),
            }
    return {}
#creates a new patient record for a nurse with the provided details
def create_patient_record_nurse(record_id, patient_id, timestamp, conditions, medications, remark):
    from app.patient import PatientRecord
    
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
    return new_record
#retrieves all records for a patient, formatted for doctor viewing
def view_patient_records_doctor(patient_id):
    "View all records for a patient"

    from app.schedule import ScheduleManager
    manager = ScheduleManager()

    patient=manager.find_patient_by_id(patient_id)
    if not patient:
        return False,"Patient Not Found", None
    records=[r for r in manager.records if r.p_id == patient_id]

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
#formats a list of patient records for nurse viewing
def view_patient_records_nurse(records):
    results = [{
            "record_id": r.pr_record_id,
            "timestamp": r.pr_timestamp,
            "conditions": r.pr_conditions,
            "medications": r.pr_medications,
            "remark": r.pr_remark
        } for r in records]
    
    return results
# updates a patient record for a doctor with specified fields, including validation
def update_record_doctor(p_id, record_id, **kwargs):
   
    from app.schedule import ScheduleManager
    manager = ScheduleManager()

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
#updates a patient record for a nurse with specified fields
def update_patient_record_nurse(record_id, conditions=None, medications=None, remark=None):
    from app.schedule import ScheduleManager
    manager = ScheduleManager()
    if conditions is not None:
        manager.record.pr_conditions = conditions
    if medications is not None:
        manager.record.pr_medications = medications
    if remark is not None:
        manager.record.pr_remark = remark
    return True
#deletes a patient record by ID, logging the action
def delete_patient_record_doctor(record_id):
    """Delete patient record"""

    from app.schedule import ScheduleManager
    manager = ScheduleManager()

    record = next((r for r in manager.records if r.pr_record_id == record_id), None)
    if not record:
        return False, "Record not found", None
    
    manager.records.remove(record)
    manager.save()
    
    utils.log_event(f"Nurse deleted record {record_id}", "INFO")
    return True, "Record deleted successfully", record_id
#Updates a patient record for a doctor with specified fields
def update_patient_record_doctor(record_id, conditions=None, medications=None, billings=None, prediction_result=None, confidence_score=None):
    from app.schedule import ScheduleManager
    manager = ScheduleManager()
    record = next((r for r in manager.records if r.pr_record_id == record_id), None)
    if not record:
        return False, "Record not found"

    if conditions is not None:
        record.pr_conditions = conditions
    if medications is not None:
        record.pr_medications = medications
    if billings is not None:
        try:
            record.pr_billings = float(billings)
        except (TypeError, ValueError):
            return False, "Invalid billings value; must be a number"
    if prediction_result is not None:
        record.pr_prediction_result = prediction_result
    if confidence_score is not None:
        try:
            record.pr_confidence_score = float(confidence_score)
        except (TypeError, ValueError):
            return False, "Invalid confidence score; must be a number"

    try:
        manager.save()
    except Exception:
        _persist()
    return True, "Record updated successfully"

def update_record_receptionist(manager, pr_id, amount):
    current_record = next((r for r in manager.records if r.pr_record_id == pr_id), None)
    if not current_record:
        return False
    else:
        current_record.pr_billings = amount
        manager.save()
        return f"Appointment {pr_id} successfully updated with billings RM{amount}"
#wxports a patient record to a formatted text file
def print_record(manager, user, record):
    from helper_manager.profile_manager import find_age

    folder_path = "record_report"
    os.makedirs(folder_path, exist_ok=True)
    file_dir = os.path.join(folder_path, f"{record.pr_record_id}.txt")

    patient = next((p for p in manager.patients if p.p_id == record.p_id), None)
    doctor = next((d for d in manager.doctors if d.d_id == record.d_id), None)

    with open(file_dir, 'w', encoding="utf-8") as f:
        f.write("+" + "=" * 70 + "+\n")
        f.write("|{:^70}|\n".format("CARELOG - MEDICAL RECORD REPORT"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Record ID", record.pr_record_id))
        f.write("| {:25} {:<43}|\n".format("Patient ID", getattr(patient, "p_id", "")))
        f.write("| {:25} {:<43}|\n".format("Patient Name", getattr(patient, "name", "")))
        f.write("| {:25} {:<43}|\n".format("Patient Age", find_age(getattr(patient, "bday", ""))))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Doctor ID", getattr(doctor, "d_id", "")))
        f.write("| {:25} {:<43}|\n".format("Doctor Name", getattr(doctor, "name", "")))
        f.write("| {:25} {:<43}|\n".format("Department", getattr(doctor, "department", "")))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Date & Time", str(record.pr_timestamp)))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Conditions", record.pr_conditions))
        f.write("| {:25} {:<43}|\n".format("Medications", record.pr_medications))
        f.write("| {:25} {:<43}|\n".format("Billings (RM)", f"{record.pr_billings:.2f}"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Prediction Result", record.pr_prediction_result))
        f.write("| {:25} {:<43}|\n".format("Confidence Score", f"{record.pr_confidence_score:.2%}"))
        f.write("+" + "=" * 70 + "+\n")
        f.write("| {:25} {:<43}|\n".format("Remark", record.remark))
        f.write("+" + "=" * 70 + "+\n")

    utils.log_event(f"[{actor_role}] {actor_username} exported record {record.pr_record_id}", "INFO")
    return True, "Record exported successfully.", file_dir