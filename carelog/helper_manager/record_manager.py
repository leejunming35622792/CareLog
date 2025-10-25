import os
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import app.utils as utils
from app.schedule import ScheduleManager

# Single schedule manager reference (compatible with your current pattern)
_manager = ScheduleManager()

# ---- best-effort persistence, reusing your original helper ----
def _persist():
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


class RecordManager:
    """
    Universal, role-aware record helper.

    Roles: patient, doctor, nurse, receptionist, admin

    Policy (practical, privacy-friendly):
      - admin: full access
      - doctor: may view/create/update records for their patients (linked by any appointment)
      - nurse: may view/create/update records; no delete
      - receptionist: may not view clinical details (can only see identities elsewhere)
      - patient: may view their own records; no create/update/delete
    """

    ROLES = {"patient", "doctor", "nurse", "receptionist", "admin"}

    def __init__(self, schedule_manager: ScheduleManager):
        self.sc = schedule_manager

    # ---------- Public API ----------

    def search_record(
        self,
        actor_role: str,
        actor_username: str,
        p_id: str,
        record_id: str,
        *,
        enforce_relationship: bool = True,
    ) -> Dict[str, Any]:
        rec = self._get_record(record_id, p_id)
        if not rec:
            return {}
        if not self._can_view_record(actor_role, actor_username, rec, enforce_relationship=enforce_relationship):
            return {}
        return self._display_record(rec)

    def list_records(
        self,
        actor_role: str,
        actor_username: str,
        patient_id: str,
        *,
        enforce_relationship: bool = True,
    ) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        patient = self._get_patient(patient_id)
        if not patient:
            return False, "Patient not found", None

        # receptionist cannot view clinical content
        if actor_role == "receptionist":
            return False, "Access denied", None

        if not self._can_view_patient(actor_role, actor_username, patient, enforce_relationship=enforce_relationship):
            return False, "Access denied", None

        rows = [self._display_record(r) for r in self.sc.records if str(getattr(r, "p_id", "")) == str(patient_id)]
        if not rows:
            return False, f"No records found for patient {patient_id}", None
        rows.sort(key=lambda x: str(x.get("timestamp", "")))
        return True, f"Found {len(rows)} record(s)", rows

    def view_record(
        self,
        actor_role: str,
        actor_username: str,
        patient_id: str,
        record_id: str,
        *,
        enforce_relationship: bool = True,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]]:
        rec = self._get_record(record_id, patient_id)
        if not rec:
            return False, "Record not found", None
        if not self._can_view_record(actor_role, actor_username, rec, enforce_relationship=enforce_relationship):
            return False, "Access denied", None
        return True, "Record retrieved", self._display_record(rec)

    def create_record(
        self,
        actor_role: str,
        actor_username: str,
        patient_id: str,
        *,
        record_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        conditions: Any = None,
        medications: Any = None,
        remark: str = "",
        billings: Optional[float] = None,
        prediction_result: Optional[str] = None,
        confidence_score: Optional[float] = None,
    ) -> Tuple[bool, str, Optional[Any]]:
        role = (actor_role or "").lower().strip()
        self._ensure_role(role)

        if role == "receptionist":
            return False, "Receptionists cannot create clinical records", None
        if role == "patient":
            return False, "Patients cannot create clinical records", None

        patient = self._get_patient(patient_id)
        if not patient:
            return False, "Patient not found", None

        if role == "doctor":
            doc = self._get_doctor_by_username(actor_username)
            if not doc or not self._has_doctor_patient_link(doc.d_id, patient_id):
                return False, "Access denied: no doctor-patient relationship", None

        # instantiate PatientRecord
        from app.patient import PatientRecord
        rid = record_id or self._next_record_id()
        if self._get_record(rid, patient_id):
            return False, f"Record {rid} already exists", None

        ts = timestamp or dt.datetime.now().isoformat(timespec="seconds")

        new_record = PatientRecord(
            pr_record_id=rid,
            p_id=patient_id,
            pr_timestamp=ts,
            pr_conditions=conditions if conditions is not None else {},
            pr_medications=list(medications) if isinstance(medications, (list, tuple)) else [],
            pr_billings=float(billings) if billings is not None else 0.0,
            pr_prediction_result=prediction_result or "",
            pr_confidence_score=float(confidence_score) if confidence_score is not None else 0.0,
            pr_remark=remark or "",
        )

        self.sc.records.append(new_record)
        self._save()
        utils.log_event(f"[{role}] {actor_username} created record {rid} for patient {patient_id}", "INFO")
        return True, f"Record {rid} created", new_record

    def update_record(
        self,
        actor_role: str,
        actor_username: str,
        p_id: str,
        record_id: str,
        **kwargs,
    ) -> Tuple[bool, str]:
        role = (actor_role or "").lower().strip()
        self._ensure_role(role)

        rec = self._get_record(record_id, p_id)
        if not rec:
            return False, "Record not found"

        if not self._can_edit_record(role, actor_username, rec):
            return False, "Access denied"

        # validations (only apply if provided)
        if "pr_conditions" in kwargs:
            pc = kwargs["pr_conditions"]
            if not isinstance(pc, dict) or not all(isinstance(k, str) for k in pc.keys()):
                return False, "Invalid pr_conditions: expected dict[str, str]"
            rec.pr_conditions = pc

        if "pr_medications" in kwargs:
            pm = kwargs["pr_medications"]
            if isinstance(pm, (list, tuple)) and all(isinstance(x, str) for x in pm):
                rec.pr_medications = list(pm)
            else:
                return False, "Invalid pr_medications: expected list[str]"

        if "pr_billings" in kwargs:
            try:
                rec.pr_billings = float(kwargs["pr_billings"])
            except (TypeError, ValueError):
                return False, "Invalid billings: expected a number"

        if "pr_prediction_result" in kwargs:
            rec.pr_prediction_result = kwargs["pr_prediction_result"]

        if "pr_confidence_score" in kwargs:
            try:
                rec.pr_confidence_score = float(kwargs["pr_confidence_score"])
            except (TypeError, ValueError):
                return False, "Invalid confidence score: expected a number"

        if "pr_remark" in kwargs:
            rec.pr_remark = kwargs["pr_remark"]

        self._save()
        utils.log_event(f"[{role}] {actor_username} updated record {record_id} for patient {p_id}", "INFO")
        return True, "Record updated"

    def delete_record(
        self,
        actor_role: str,
        actor_username: str,
        record_id: str,
    ) -> Tuple[bool, str, Optional[str]]:
        role = (actor_role or "").lower().strip()
        self._ensure_role(role)

        if role not in {"admin", "doctor"}:
            return False, "Only admin/doctor may delete records", None

        # locate
        rec = next((r for r in self.sc.records if getattr(r, "pr_record_id", None) == record_id), None)
        if not rec:
            return False, "Record not found", None

        # for doctor, ensure relationship with patient
        if role == "doctor":
            doc = self._get_doctor_by_username(actor_username)
            if not doc or not self._has_doctor_patient_link(doc.d_id, getattr(rec, "p_id", "")):
                return False, "Access denied: no doctor-patient relationship", None

        self.sc.records.remove(rec)
        self._save()
        utils.log_event(f"[{role}] {actor_username} deleted record {record_id}", "INFO")
        return True, "Record deleted successfully", record_id

    def print_record(
        self,
        actor_role: str,
        actor_username: str,
        record_id: str,
    ) -> Tuple[bool, str, Optional[str]]:
        # view permission implies print permission
        rec = next((r for r in self.sc.records if getattr(r, "pr_record_id", None) == record_id), None)
        if not rec:
            return False, "Record not found", None

        if not self._can_view_record(actor_role, actor_username, rec):
            return False, "Access denied", None

        p = self._get_patient(getattr(rec, "p_id", ""))
        folder = "record_report"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{rec.pr_record_id}.txt")

        remark = getattr(rec, "pr_remark", "") or ""
        if len(remark) > 60:
            remark = remark[:57].rstrip() + "..."

        with open(path, "w", encoding="utf-8") as f:
            f.write("+" + "=" * 70 + "+\n")
            f.write("|{:^70}|\n".format("CARELOG - PATIENT RECORD"))
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Record ID", str(rec.pr_record_id)))
            f.write("| {:25} {:<43}|\n".format("Patient ID", str(getattr(p, "p_id", ""))))
            f.write("| {:25} {:<43}|\n".format("Name", str(getattr(p, "name", ""))))
            f.write("| {:25} {:<43}|\n".format("Timestamp", str(getattr(rec, "pr_timestamp", ""))))
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Conditions", self._fmt_conditions(getattr(rec, "pr_conditions", {}))))
            f.write("| {:25} {:<43}|\n".format("Medications", ", ".join(getattr(rec, "pr_medications", []) or [])))
            f.write("| {:25} {:<43}|\n".format("Billings", str(getattr(rec, "pr_billings", 0.0))))
            f.write("| {:25} {:<43}|\n".format("Prediction", str(getattr(rec, "pr_prediction_result", ""))))
            f.write("| {:25} {:<43}|\n".format("Confidence", str(getattr(rec, "pr_confidence_score", ""))))
            f.write("| {:25} {:<43}|\n".format("Remark", remark))
            f.write("+" + "=" * 70 + "+\n")

        utils.log_event(f"[{actor_role}] {actor_username} printed record {record_id}", "INFO")
        return True, "Record exported", path

    # ---------- Internals ----------

    def _save(self):
        try:
            if hasattr(self.sc, "save"):
                self.sc.save()
            elif hasattr(self.sc, "save_to_json"):
                self.sc.save()
            else:
                _persist()
        except Exception:
            _persist()

    def _ensure_role(self, role: str):
        if role not in self.ROLES:
            raise ValueError(f"Unknown role '{role}'")

    def _get_patient(self, patient_id: str) -> Optional[Any]:
        # try ScheduleManager API first
        try:
            found, msg, patient = self.sc.find_patient_by_id(patient_id)
            if found:
                return patient
        except Exception:
            pass
        return next((p for p in self.sc.patients if str(getattr(p, "p_id", "")) == str(patient_id)), None)

    def _get_doctor_by_username(self, username: str) -> Optional[Any]:
        return next((d for d in self.sc.doctors if getattr(d, "username", None) == username), None)

    def _has_doctor_patient_link(self, doctor_id: str, patient_id: str) -> bool:
        for a in getattr(self.sc, "appointments", []):
            if getattr(a, "d_id", None) == doctor_id and getattr(a, "p_id", None) == patient_id:
                return True
        return False

    def _get_record(self, record_id: str, p_id: str) -> Optional[Any]:
        return next(
            (r for r in self.sc.records
             if str(getattr(r, "pr_record_id", "")) == str(record_id)
             and str(getattr(r, "p_id", "")) == str(p_id)),
            None,
        )

    def _can_view_patient(
        self,
        actor_role: str,
        actor_username: str,
        patient: Any,
        *,
        enforce_relationship: bool = True,
    ) -> bool:
        role = (actor_role or "").lower().strip()
        if role == "admin":
            return True
        if role == "patient":
            return getattr(patient, "username", None) == actor_username
        if role == "nurse":
            return True
        if role == "doctor":
            if not enforce_relationship:
                return True
            doc = self._get_doctor_by_username(actor_username)
            return bool(doc and self._has_doctor_patient_link(doc.d_id, getattr(patient, "p_id", "")))
        return False

    def _can_view_record(
        self,
        actor_role: str,
        actor_username: str,
        rec: Any,
        *,
        enforce_relationship: bool = True,
    ) -> bool:
        role = (actor_role or "").lower().strip()
        if role == "admin":
            return True
        p = self._get_patient(getattr(rec, "p_id", ""))
        if role == "patient":
            return bool(p and getattr(p, "username", None) == actor_username)
        if role == "nurse":
            return True
        if role == "doctor":
            if not enforce_relationship:
                return True
            doc = self._get_doctor_by_username(actor_username)
            return bool(doc and self._has_doctor_patient_link(doc.d_id, getattr(rec, "p_id", "")))
        return False

    def _can_edit_record(self, actor_role: str, actor_username: str, rec: Any) -> bool:
        role = (actor_role or "").lower().strip()
        if role == "admin":
            return True
        if role == "nurse":
            return True
        if role == "doctor":
            doc = self._get_doctor_by_username(actor_username)
            return bool(doc and self._has_doctor_patient_link(doc.d_id, getattr(rec, "p_id", "")))
        return False

    @staticmethod
    def _fmt_conditions(conds: Any) -> str:
        if isinstance(conds, dict):
            return ", ".join([f"{k}: {v}" for k, v in conds.items()])
        if isinstance(conds, (list, tuple, set)):
            return ", ".join([str(x) for x in conds])
        return str(conds or "")

    def _display_record(self, r: Any) -> Dict[str, Any]:
        return {
            "record_id": getattr(r, "pr_record_id", ""),
            "patient_id": getattr(r, "p_id", ""),
            "timestamp": getattr(r, "pr_timestamp", ""),
            "conditions": getattr(r, "pr_conditions", {}),
            "medications": getattr(r, "pr_medications", []),
            "billings": getattr(r, "pr_billings", 0.0),
            "prediction_result": getattr(r, "pr_prediction_result", ""),
            "confidence_score": getattr(r, "pr_confidence_score", 0.0),
            "remark": getattr(r, "pr_remark", ""),
        }

    def _next_record_id(self) -> str:
        # naive ID generator: R0001 + 1
        existing = [str(getattr(r, "pr_record_id", "")) for r in self.sc.records]
        nums = []
        for rid in existing:
            try:
                if rid and rid[0] in {"R", "r"}:
                    nums.append(int(rid[1:]))
            except Exception:
                continue
        nxt = (max(nums) + 1) if nums else 1
        return f"R{nxt:04d}"


# Instantiate universal manager
_record_mgr = RecordManager(_manager)

# -------------------- Legacy wrappers (keep current pages working) --------------------
# These mirror your original function names/signatures and delegate to the universal manager.

def search_record(p_id, record_id):
    # Legacy had no actor; allow admin-equivalent view
    return _record_mgr.search_record("admin", "system", str(p_id), str(record_id), enforce_relationship=False)

def create_patient_record_nurse(record_id, patient_id, timestamp, conditions, medications, remark):
    # Strict RBAC: nurse is allowed to create
    ok, msg, rec = _record_mgr.create_record(
        "nurse", "nurse@system", str(patient_id),
        record_id=str(record_id),
        timestamp=str(timestamp),
        conditions=conditions,
        medications=medications,
        remark=remark,
    )
    return rec if ok else None

def view_patient_records_doctor(patient_id):
    ok, msg, rows = _record_mgr.list_records("doctor", "doctor@system", str(patient_id), enforce_relationship=False)
    return (ok, msg, rows)

def view_patient_records_nurse(records):
    # Kept as a pure formatting helper for a provided list of record objects
    results = [{
        "record_id": r.pr_record_id,
        "timestamp": r.pr_timestamp,
        "conditions": r.pr_conditions,
        "medications": r.pr_medications,
        "remark": r.pr_remark
    } for r in records]
    return results

def update_record_doctor(p_id, record_id, **kwargs):
    ok, msg = _record_mgr.update_record("doctor", "doctor@system", str(p_id), str(record_id), **kwargs)
    if ok:
        _persist()
    return ok

def update_patient_record_nurse(record_id, conditions=None, medications=None, remark=None):
    # Fixed bug: was writing to manager.record (singular). Now find by ID.
    rec = next((r for r in _manager.records if str(getattr(r, "pr_record_id", "")) == str(record_id)), None)
    if not rec:
        return False
    payload = {}
    if conditions is not None:
        payload["pr_conditions"] = conditions
    if medications is not None:
        payload["pr_medications"] = medications
    if remark is not None:
        payload["pr_remark"] = remark
    ok, msg = _record_mgr.update_record("nurse", "nurse@system", getattr(rec, "p_id", ""), str(record_id), **payload)
    return ok

def delete_patient_record_doctor(record_id):
    ok, msg, rid = _record_mgr.delete_record("doctor", "doctor@system", str(record_id))
    if not ok:
        return False, msg, None
    return True, "Record deleted successfully", rid

def update_patient_record_doctor(record_id, conditions=None, medications=None, billings=None, prediction_result=None, confidence_score=None):
    rec = next((r for r in _manager.records if str(getattr(r, "pr_record_id", "")) == str(record_id)), None)
    if not rec:
        return False, "Record not found"
    p_id = getattr(rec, "p_id", "")
    payload = {}
    if conditions is not None:
        payload["pr_conditions"] = conditions
    if medications is not None:
        payload["pr_medications"] = medications
    if billings is not None:
        payload["pr_billings"] = billings
    if prediction_result is not None:
        payload["pr_prediction_result"] = prediction_result
    if confidence_score is not None:
        payload["pr_confidence_score"] = confidence_score
    ok, msg = _record_mgr.update_record("doctor", "doctor@system", str(p_id), str(record_id), **payload)
    if not ok:
        return False, msg
    return True, "Record updated successfully"

def print_record(*args, **kwargs):
    """
    Export a clinical record to a text file (record_report/<record_id>.txt).

    Flexible call patterns:
        print_record("R0001")
        print_record(record_id="R0001")
        print_record(role="doctor", username="dr_lee", record_id="R0001")
        print_record(actor_role="nurse", actor_username="nurse_amy", record_id="R0001")

    Returns:
        (ok: bool, message: str, path_or_none: str|None)
    """
    # Defaults keep old, parameterless calls from crashing, but require a record_id.
    actor_role = (
        kwargs.get("role")
        or kwargs.get("actor_role")
        or "admin"
    )
    actor_username = (
        kwargs.get("username")
        or kwargs.get("actor_username")
        or "system"
    )

    # record_id from kwargs or first positional
    record_id = kwargs.get("record_id")
    if record_id is None and args:
        record_id = args[0]

    if not record_id:
        return False, "record_id required", None

    return _record_mgr.print_record(str(actor_role).lower(), str(actor_username), str(record_id))