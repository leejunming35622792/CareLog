import datetime
from app.schedule import ScheduleManager
from app.remark import PatientRemark
import app.utils as utils

manager = ScheduleManager()

def add_patient_remark(patient_id :int , doctor_username: str, remark_type: str, remark_content :str):
    patient=next((p for p in manager.patients if p.p_id==patient_id), None)
    if patient is None:
        return False, "Patient Not Found", None
    doctor=next((d for d in manager.doctors if d.username == doctor_username), None)
    if doctor is None:
        return False, "Doctor Not Found", None
    valid_types=["mood", "pain_level","dietary","general","observation"]
    r_type=remark_type.strip().lower()
    if r_type not in valid_types:
        return False, f" Invalid Remark Type. Must be one of : {', '.join (valid_types)}", None
    remark_id = f"RM{manager.next_remark_id:04d}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_remark=PatientRemark(
        remark_id=remark_id,
        patient_id=patient_id,
        doctor_id=doctor.d_id,
        timestamp=timestamp,
        remark_type=r_type,
        content=remark_content,
        is_active=True,
        last_modified=timestamp
    )
    manager.remarks.append(new_remark)
    rid=manager.next_remark_id
    manager.next_remark_id+=1
    manager._save_data()
    return True, "Remark added successfully", remark_id

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
        is_active   = True,
        last_modified = timestamp
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

def edit_patient_remark(remark_id: str, doctor_username: str, new_content: str):
    remark = next((rm for rm in manager.remarks if str(rm.remark_id) == str(remark_id)), None)
    if remark is None:
        return False, "Remark not found"

    doc = next((d for d in manager.doctors if d.username == doctor_username), None)
    if doc is None:
        return False, "Doctor not found"

    if remark.doctor_id != doc.d_id:
        return False, "You can only edit your own remarks"

    remark.update_content(new_content)
    manager._save_data()
    return True, "Remark updated successfully"


def view_patient_remarks(patient_id: int, remark_type: str | None = None, limit: int | None = None):
    patient = manager.find_patient_by_id(patient_id)
    if patient is None:
        return False, "Patient not found", []

    items = [rm for rm in manager.remarks if rm.patient_id == patient_id and rm.is_active]
    if remark_type:
        items = [rm for rm in items if rm.remark_type == remark_type]

    def _key(rm):
        try:
            return datetime.datetime.strptime(rm.timestamp, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return rm.timestamp
    items.sort(key=_key, reverse=True)

    if limit:
        items = items[:limit]
    out = []
    for rm in items:
        doc = manager.find_doctor_by_id(rm.doctor_id) if getattr(rm, "doctor_id", None) else None
        out.append({
            "remark_id": rm.remark_id,
            "doctor_id": getattr(rm, "doctor_id", None),
            "doctor_name": (doc.name if doc else ("Nurse" if getattr(rm, "doctor_id", None) is None else "Unknown Doctor")),
            "timestamp": rm.timestamp,
            "remark_type": rm.remark_type,
            "content": rm.content,
            "last_modified": getattr(rm, "last_modified", rm.timestamp),
        })
    return True, f"Found {len(out)} remarks", out

def get_remarks_by_type(patient_id: int, remark_type: str):
        return manager.view_patient_remarks(patient_id, remark_type=remark_type)
    
def get_recent_patient_remarks(patient_id: int, days: int = 7):
    patient = manager.find_patient_by_id(patient_id)
    if patient is None:
        return False, "Patient not found", []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    recent = []
    for rm in manager.remarks:
        if rm.patient_id == patient_id and rm.is_active:
            try:
                dt = datetime.datetime.strptime(rm.timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if dt >= cutoff:
                if getattr(rm, "doctor_id", None):
                    doc = manager.find_doctor_by_id(rm.doctor_id)
                    doctor_name = doc.name if doc else "Unknown Doctor"
                else:
                    doctor_name = "Nurse"
                recent.append({
                    "remark_id": rm.remark_id,
                    "doctor_name": doctor_name,
                    "timestamp": rm.timestamp,
                    "remark_type": rm.remark_type,
                    "content": rm.content,
                })
    def _k(x):
        try:
            return datetime.datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return x["timestamp"]
    recent.sort(key=_k, reverse=True)
    return True, f"Found {len(recent)} remarks from last {days} days", recent
    