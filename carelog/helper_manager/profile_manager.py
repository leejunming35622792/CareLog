import datetime
from app.schedule import ScheduleManager
import app.utils as utils

manager = ScheduleManager()

def find_age(bday):
    # Get current year
    today = datetime.datetime.now().year
    # Get birth year
    birth_year = datetime.datetime.fromisoformat(bday)
    # Find age
    age = today - birth_year.year
    # Return age
    return age

def view_doctor_details(username):
        doctor = next((d for d in manager.doctors if d.username == username), None)

        if doctor is None:
            return False, "Doctor Not Found", None
        
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
        return True, "Profile Successfully Retrieved", profile

def view_patient_details_by_doctor(patient_id: int):
    # be tolerant of caller passing int or string IDs (compare as strings)
    patient = next((p for p in manager.patients if str(p.p_id) == str(patient_id)), None)
    if patient is None:
        return False, "Patient Not Found", None

    # records use attribute `p_id` (see record_manager.py), not `patient`
    patient_records = [r for r in manager.records if str(getattr(r, "p_id", "")) == str(patient_id)]

    previous_conditions: list[str] = []
    medication_history: list[str] = []

    for record in patient_records:
        # --- previous conditions ---
        pr_conds = getattr(record, "pr_conditions", None)
        if pr_conds:
            if isinstance(pr_conds, (list, tuple, set)):
                previous_conditions.extend([str(x).strip() for x in pr_conds if str(x).strip()])
            elif isinstance(pr_conds, dict):
                previous_conditions.extend([f"{k}: {v}" for k, v in pr_conds.items()])
            elif isinstance(pr_conds, str):
                # if comma-separated string, split into items; otherwise treat whole string as one item
                if "," in pr_conds:
                    previous_conditions.extend([p.strip() for p in pr_conds.split(",") if p.strip()])
                else:
                    previous_conditions.append(pr_conds.strip())
            else:
                previous_conditions.append(str(pr_conds))

        # --- medication history ---
        pr_meds = getattr(record, "pr_medications", None)
        if pr_meds:
            if isinstance(pr_meds, (list, tuple, set)):
                medication_history.extend([str(x).strip() for x in pr_meds if str(x).strip()])
            elif isinstance(pr_meds, dict):
                medication_history.extend([f"{k}: {v}" for k, v in pr_meds.items()])
            elif isinstance(pr_meds, str):
                if "," in pr_meds:
                    medication_history.extend([m.strip() for m in pr_meds.split(",") if m.strip()])
                else:
                    medication_history.append(pr_meds.strip())
            else:
                medication_history.append(str(pr_meds))

    # remove duplicates but keep order
    previous_conditions = list(dict.fromkeys(previous_conditions))
    medication_history = list(dict.fromkeys(medication_history))

    info = {
        "patient_id": patient.p_id,
        "name": patient.name,
        "gender": patient.gender,
        "date_of_birth": getattr(patient, "date_of_birth", ""),
        "previous_conditions": previous_conditions,
        "medication_history": medication_history,
    }
    return True, "Patient details retrieved successfully", info

def view_nurse_details(username, password):
        nurse = next((n for n in manager.nurses if n.username == username), None)
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

def view_patient_details_by_nurse(patient_id):
    """View patient details including records and remarks"""
    found, msg, patient = manager.find_patient_by_id(patient_id)
    
    if not found:
        return False, msg, None

    patient_records = [r for r in manager.records if r.p_id == patient_id]
    patient_remarks = [r for r in manager.remarks if r.patient_id == patient_id and r.is_active]
    
    if patient is None:
        return False, "Patient not found", None

    patient_info = {
        "patient_id": patient.p_id,
        "name": patient.name,
        "gender": patient.gender,
        "email": getattr(patient, "email", None),
        "contact": getattr(patient, "contact_num", None),
        "address": getattr(patient, "address", None),
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

def search_and_select_profile(manager):
        role = input("Search for (patient/doctor/nurse/receptionist): ").strip().lower()
        role_map = {
        "patient": (manager.patients, "p_id"),
        "doctor": (manager.doctors, "d_id"),
        "nurse": (manager.nurses, "n_id"),
        "receptionist": (manager.receptionists, "r_id"),
        }
        if role not in role_map:
            print("Invalid role. Please enter patient/doctor/nurse/receptionist.")
            return False, None

        items, id_attr = role_map[role]
        name_query = input("Enter name (partial is okay): ").strip().lower()
        matches = [obj for obj in items if name_query in getattr(obj, "name", "").lower()]

        if not matches:
            print(f"No {role} found matching '{name_query}'.")
            return False, None

        print(f"\nFound {len(matches)} {role}(s):")
        for obj in matches:
            pid = getattr(obj, id_attr)
            print(f"- {pid}: {obj.name}")

        selected_id = input(f"\nEnter the exact {role.capitalize()} ID to view (e.g., P0001/N0003): ").strip().upper()
        selected = next((o for o in matches if getattr(o, id_attr).upper() == selected_id), None)

        if not selected:
            print("No profile found with that ID in the above results.")
            return False, None

        print("\n--- Profile ---")
        for k, v in selected.__dict__.items():
            if k == "password":
                continue
            print(f"{k}: {v}")

        return True, selected

def search_patient_by_name(name):
    """Search patients by name"""
    if not name or not name.strip():
        return False, "Please provide a name to search", None
    
    matching_patients = [
        p for p in manager.patients 
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