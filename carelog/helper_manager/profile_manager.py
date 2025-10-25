import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.schedule import ScheduleManager
import app.utils as utils

manager = ScheduleManager()

# ---------- Utilities ----------

def find_age(bday: str) -> int:
    """
    Robust age calculation from ISO-like date string.
    Accepts 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' etc.
    """
    try:
        dt = datetime.datetime.fromisoformat(str(bday))
    except Exception:
        return 0
    today = datetime.date.today()
    years = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
    return years


def _val(x: Any, *keys: str, default: Any = "") -> Any:
    """
    Return first present attribute from keys on object x, else default.
    Example: _val(patient, "date_of_birth", "bday", default="")
    """
    for k in keys:
        if hasattr(x, k):
            return getattr(x, k)
    return default


# ---------- Universal Profile Manager ----------

class ProfileManager:
    """
    A role-aware, universal profile/lookup helper.

    Roles recognized: patient, doctor, nurse, receptionist, admin

    Key rules implemented:
      - Everyone can view their *own* profile.
      - Doctors can view patient clinical details only if they have a past or current appointment
        link with that patient.
      - Nurses can view patient clinical details.
      - Receptionists can *identify* patients (personal/contact info, counts), but are restricted
        from clinical record contents by default (privacy).
      - Admin can view anything.

    This is designed to match your SRS’ intent while staying pragmatic with the current codebase.
    """

    ROLES = {"patient", "doctor", "nurse", "receptionist", "admin"}

    def __init__(self, schedule_manager: ScheduleManager):
        self.sc = schedule_manager

    # -------- Public, role-aware API --------

    def view_user_profile(
        self,
        actor_role: str,
        actor_username: str,
        subject_role: Optional[str] = None,
        *,
        subject_id: Optional[str] = None,
        subject_username: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        View any user's profile, enforcing permissions. If subject_* not provided, defaults to actor (self-profile).
        """
        role = (actor_role or "").lower().strip()
        self._ensure_role(role)

        # Resolve subject
        if subject_role is None and subject_id is None and subject_username is None:
            subject_role = role
            subject_username = actor_username

        subject_role = (subject_role or "").lower().strip()
        self._ensure_role(subject_role)

        subject = self._get_user(subject_role, user_id=subject_id, username=subject_username)
        if not subject:
            return False, "User not found", None

        # Everybody may view their own profile
        if subject_role == role and self._user_matches(subject_role, subject, actor_username):
            return True, "Profile retrieved", self._profile_dict(subject_role, subject)

        # Cross-role viewing
        if role == "admin":
            return True, "Profile retrieved", self._profile_dict(subject_role, subject)

        if role == "receptionist":
            # Receptionists can see personal/contact details for identification
            return True, "Profile retrieved", self._profile_dict(subject_role, subject, include_clinical=False)

        if role in {"doctor", "nurse", "patient"}:
            # These roles may view *other staff* profiles (non-clinical) to show names/contact in UI.
            if subject_role in {"doctor", "nurse", "receptionist", "admin"}:
                return True, "Profile retrieved", self._profile_dict(subject_role, subject, include_clinical=False)

            if subject_role == "patient":
                if role == "nurse":
                    # Nurses can view patient’s clinical details.
                    return True, "Profile retrieved", self._patient_overview(subject)

                if role == "doctor":
                    # Doctors require relationship via appointment(s)
                    doc = self._get_user("doctor", username=actor_username)
                    if not doc:
                        return False, "Doctor not found", None
                    if not self._has_doctor_patient_link(doc.d_id, subject.p_id):
                        return False, "Access denied: no doctor-patient relationship.", None
                    return True, "Profile retrieved", self._patient_overview(subject)

                if role == "patient":
                    # Patients cannot view other patients
                    return False, "Access denied", None

        return False, "Access denied", None

    def view_patient_details(
        self,
        actor_role: str,
        actor_username: str,
        patient_id: str,
        *,
        include_records: bool = True,
        include_remarks: bool = True,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Rich patient details with clinical context (records/remarks), enforcing RBAC.
        """
        role = (actor_role or "").lower().strip()
        self._ensure_role(role)

        patient = self._get_user("patient", user_id=patient_id)
        if not patient:
            return False, "Patient not found", None

        if role == "admin":
            return True, "Patient details retrieved", self._patient_details(patient, include_records, include_remarks)

        if role == "nurse":
            return True, "Patient details retrieved", self._patient_details(patient, include_records, include_remarks)

        if role == "doctor":
            doc = self._get_user("doctor", username=actor_username)
            if not doc:
                return False, "Doctor not found", None
            if not self._has_doctor_patient_link(doc.d_id, patient.p_id):
                return False, "Access denied: no doctor-patient relationship.", None
            return True, "Patient details retrieved", self._patient_details(patient, include_records, include_remarks)

        if role == "receptionist":
            # Receptionist can *identify* patients (no clinical payload by default)
            info = self._patient_details(patient, include_records=False, include_remarks=False)
            return True, "Patient details retrieved", info

        if role == "patient":
            # Patient may view their own details
            me = self._get_user("patient", username=actor_username)
            if not me or me.p_id != patient.p_id:
                return False, "Access denied", None
            return True, "Patient details retrieved", self._patient_details(patient, include_records, include_remarks)

        return False, "Access denied", None

    def search_users(
        self,
        actor_role: str,
        actor_username: str,
        role: str,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        contact: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
    ) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        Flexible search with partial matching. RBAC:
          - admin/receptionist: may search any role
          - nurse/doctor: may search patients; other staff returned with limited (non-clinical) info
          - patient: may only search self via exact id/username (effectively useless for others)
        """
        actor_role = (actor_role or "").lower().strip()
        self._ensure_role(actor_role)

        role = (role or "").lower().strip()
        self._ensure_role(role)

        # Permission gate
        if actor_role in {"admin", "receptionist"}:
            pass
        elif actor_role in {"nurse", "doctor"}:
            if role not in {"patient", "doctor", "nurse", "receptionist"}:
                return False, "Access denied", None
        elif actor_role == "patient":
            # Patients cannot enumerate others
            if role != "patient":
                return False, "Access denied", None

        coll = self._collection(role)
        qname = (name or "").strip().lower()
        qemail = (email or "").strip().lower()
        qphone = (contact or "").strip().lower()
        qid = (user_id or "").strip().lower()

        def match(u) -> bool:
            if qid and qid not in str(_val(u, "p_id", "d_id", "n_id", "r_id")).lower():
                return False
            if qname and qname not in str(getattr(u, "name", "")).lower():
                return False
            if qemail and qemail not in str(getattr(u, "email", "")).lower():
                return False
            if qphone and qphone not in str(getattr(u, "contact_num", "")).lower():
                return False
            return True

        users = [u for u in coll if match(u)][: max(1, int(limit))]
        rows: List[Dict[str, Any]] = []

        for u in users:
            # Restrict receptionist/doctor/nurse views appropriately
            if role == "patient":
                if actor_role == "receptionist":
                    rows.append(self._patient_identity(u))
                elif actor_role == "doctor":
                    # Doctors: list all matching patients, but full details later still require relationship
                    rows.append(self._patient_identity(u))
                elif actor_role == "nurse":
                    rows.append(self._patient_identity(u))
                elif actor_role == "admin":
                    rows.append(self._patient_identity(u))
                elif actor_role == "patient":
                    me = self._get_user("patient", username=actor_username)
                    if me and me.p_id == u.p_id:
                        rows.append(self._patient_identity(u))
            else:
                rows.append(self._profile_dict(role, u, include_clinical=False))

        utils.log_event(f"[{actor_role}] search {role} name='{name}' email='{email}' contact='{contact}' id='{user_id}' -> {len(rows)}", "INFO")
        if not rows:
            return False, "No results", None
        return True, f"Found {len(rows)} result(s)", rows

    # -------- Back-compat wrappers (existing function names) --------
    # Use these until pages are migrated to the universal API.

    def _wrapper_view_doctor_details(self, username: str):
        return self.view_user_profile("doctor", username, subject_role="doctor", subject_username=username)

    def _wrapper_view_nurse_details(self, username: str, password: str):
        # NOTE: password check should be in Auth; preserved for compatibility.
        nurse = next((n for n in self.sc.nurses if getattr(n, "username", None) == username), None)
        if not nurse:
            return False, "Nurse not found", None
        if getattr(nurse, "password", None) != password:
            return False, "Incorrect password", None
        return self.view_user_profile("nurse", username, subject_role="nurse", subject_username=username)

    def _wrapper_view_patient_details_by_doctor(self, patient_id: str):
        """
        Legacy signature had no actor context; we cannot *prove* relationship.
        Prefer: view_patient_details('doctor', <doctor_username>, patient_id)
        Here we return an identification-only payload for safety.
        """
        patient = self._get_user("patient", user_id=str(patient_id))
        if not patient:
            return False, "Patient not found", None
        return True, "Patient details (limited; use universal API for full)", self._patient_identity(patient)

    def _wrapper_view_patient_details_by_nurse(self, patient_id: str):
        ok, msg, data = self.view_patient_details("nurse", "nurse@system", str(patient_id))
        return ok, msg, data

    def _wrapper_search_patient_by_name(self, name: str):
        return self.search_users("nurse", "nurse@system", "patient", name=name)

    # -------- Internals --------

    def _ensure_role(self, role: str):
        if role not in self.ROLES:
            raise ValueError(f"Unknown role '{role}'")

    def _collection(self, role: str) -> Iterable[Any]:
        return {
            "patient": self.sc.patients,
            "doctor": self.sc.doctors,
            "nurse": self.sc.nurses,
            "receptionist": self.sc.receptionists,
            "admin": self.sc.admins,
        }[role]

    def _get_user(
        self,
        role: str,
        *,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Optional[Any]:
        coll = self._collection(role)
        if user_id:
            key = {"patient": "p_id", "doctor": "d_id", "nurse": "n_id", "receptionist": "r_id", "admin": "a_id"}[role]
            return next((u for u in coll if str(getattr(u, key, "")).lower() == str(user_id).lower()), None)
        if username:
            return next((u for u in coll if getattr(u, "username", None) == username), None)
        return None

    def _user_matches(self, role: str, user: Any, username: str) -> bool:
        return getattr(user, "username", None) == username

    def _has_doctor_patient_link(self, doctor_id: str, patient_id: str) -> bool:
        """
        True if there is any appointment linking this doctor and patient (past or present).
        """
        for a in getattr(self.sc, "appointments", []):
            if getattr(a, "d_id", None) == doctor_id and getattr(a, "p_id", None) == patient_id:
                return True
        return False

    # ----- payload builders -----

    def _profile_dict(self, role: str, u: Any, *, include_clinical: bool = False) -> Dict[str, Any]:
        # shared
        base = {
            "role": role,
            "id": _val(u, "p_id", "d_id", "n_id", "r_id", "a_id", default=""),
            "name": getattr(u, "name", ""),
            "email": getattr(u, "email", ""),
            "contact_num": getattr(u, "contact_num", ""),
            "address": getattr(u, "address", ""),
            "gender": getattr(u, "gender", ""),
            "date_of_birth": _val(u, "date_of_birth", "bday", default=""),
            "date_joined": getattr(u, "date_joined", ""),
        }
        # computed
        base["age"] = find_age(base["date_of_birth"]) if base["date_of_birth"] else 0

        # role-specific visible fields (non-clinical only)
        if role in {"doctor", "nurse"}:
            base["department"] = getattr(u, "department", "")
            base["speciality"] = getattr(u, "speciality", "")
        if role == "nurse":
            base["with_doctor"] = getattr(u, "with_doctor", "")
        return base

    def _patient_identity(self, patient: Any) -> Dict[str, Any]:
        """
        Non-clinical identity snapshot for receptionist/doctor/nurse/admin searches.
        """
        return {
            "patient_id": getattr(patient, "p_id", ""),
            "name": getattr(patient, "name", ""),
            "gender": getattr(patient, "gender", ""),
            "email": getattr(patient, "email", ""),
            "contact_num": getattr(patient, "contact_num", ""),
            "address": getattr(patient, "address", ""),
            "date_of_birth": _val(patient, "date_of_birth", "bday", default=""),
            "age": find_age(_val(patient, "date_of_birth", "bday", default="")),
        }

    def _patient_overview(self, patient: Any) -> Dict[str, Any]:
        """
        Clinical *overview* used for role-appropriate views.
        (Keeps the rich lists for nurse/doctor while avoiding PII sprawl elsewhere.)
        """
        prev_conds, meds = self._collect_history(patient)
        return {
            "patient_id": getattr(patient, "p_id", ""),
            "name": getattr(patient, "name", ""),
            "gender": getattr(patient, "gender", ""),
            "date_of_birth": _val(patient, "date_of_birth", "bday", default=""),
            "age": find_age(_val(patient, "date_of_birth", "bday", default="")),
            "previous_conditions": prev_conds,
            "medication_history": meds,
        }

    def _patient_details(self, patient: Any, include_records: bool, include_remarks: bool) -> Dict[str, Any]:
        prev_conds, meds = self._collect_history(patient)

        payload: Dict[str, Any] = {
            "patient_id": getattr(patient, "p_id", ""),
            "name": getattr(patient, "name", ""),
            "gender": getattr(patient, "gender", ""),
            "email": getattr(patient, "email", None),
            "contact": getattr(patient, "contact_num", None),
            "address": getattr(patient, "address", None),
            "date_of_birth": _val(patient, "date_of_birth", "bday", default=""),
            "age": find_age(_val(patient, "date_of_birth", "bday", default="")),
            "previous_conditions": prev_conds,
            "medication_history": meds,
        }

        if include_records:
            records = [r for r in getattr(self.sc, "records", []) if str(getattr(r, "p_id", "")) == str(getattr(patient, "p_id", ""))]
            payload["records_count"] = len(records)
            payload["records"] = [
                {
                    "record_id": getattr(r, "pr_record_id", ""),
                    "timestamp": getattr(r, "pr_timestamp", ""),
                    "conditions": getattr(r, "pr_conditions", ""),
                    "medications": getattr(r, "pr_medications", ""),
                    "remark": getattr(r, "pr_remark", ""),
                }
                for r in records
            ]

        if include_remarks:
            remarks = [
                r for r in getattr(self.sc, "remarks", [])
                if getattr(r, "patient_id", None) == getattr(patient, "p_id", None) and getattr(r, "is_active", False)
            ]
            payload["remarks_count"] = len(remarks)
            payload["remarks"] = [
                {
                    "remark_id": getattr(r, "remark_id", ""),
                    "doctor_id": getattr(r, "doctor_id", ""),
                    "timestamp": getattr(r, "timestamp", ""),
                    "type": getattr(r, "remark_type", ""),
                    "content": getattr(r, "content", ""),
                }
                for r in remarks
            ]

        return payload

    def _collect_history(self, patient: Any) -> Tuple[List[str], List[str]]:
        """
        Collate previous_conditions and medication_history from records, de-duplicated but order-preserving.
        """
        pid = str(getattr(patient, "p_id", ""))
        patient_records = [r for r in getattr(self.sc, "records", []) if str(getattr(r, "p_id", "")) == pid]

        previous_conditions: List[str] = []
        medication_history: List[str] = []

        for record in patient_records:
            # previous conditions
            pr_conds = getattr(record, "pr_conditions", None)
            if pr_conds:
                self._extend_fuzzy(previous_conditions, pr_conds)
            # medications
            pr_meds = getattr(record, "pr_medications", None)
            if pr_meds:
                self._extend_fuzzy(medication_history, pr_meds)

        # de-dup, keep order
        previous_conditions = list(dict.fromkeys([x for x in previous_conditions if str(x).strip()]))
        medication_history = list(dict.fromkeys([x for x in medication_history if str(x).strip()]))
        return previous_conditions, medication_history

    @staticmethod
    def _extend_fuzzy(dst: List[str], src: Any) -> None:
        if isinstance(src, (list, tuple, set)):
            dst.extend([str(x).strip() for x in src if str(x).strip()])
        elif isinstance(src, dict):
            dst.extend([f"{k}: {v}" for k, v in src.items()])
        elif isinstance(src, str):
            if "," in src:
                dst.extend([s.strip() for s in src.split(",") if s.strip()])
            else:
                dst.append(src.strip())
        else:
            dst.append(str(src).strip())


# Instantiate the universal manager for callers
_profile_mgr = ProfileManager(manager)


# ---------- Backwards-compatible functions (existing imports keep working) ----------

def view_doctor_details(username: str):
    """
    Prefer: _profile_mgr.view_user_profile('doctor', username, subject_role='doctor', subject_username=username)
    """
    return _profile_mgr._wrapper_view_doctor_details(username)


def view_patient_details_by_doctor(patient_id: int):
    """
    Legacy signature lacked actor context; returns identification-only data for safety.
    Prefer: _profile_mgr.view_patient_details('doctor', <doctor_username>, patient_id)
    """
    return _profile_mgr._wrapper_view_patient_details_by_doctor(str(patient_id))


def view_nurse_details(username: str, password: str):
    """
    Prefer: _profile_mgr.view_user_profile('nurse', username, subject_role='nurse', subject_username=username)
    """
    return _profile_mgr._wrapper_view_nurse_details(username, password)


def view_patient_details_by_nurse(patient_id: str):
    """
    Prefer: _profile_mgr.view_patient_details('nurse', <nurse_username>, patient_id)
    """
    return _profile_mgr._wrapper_view_patient_details_by_nurse(str(patient_id))


def search_patient_by_name(name: str):
    """
    Prefer: _profile_mgr.search_users(actor_role, actor_username, 'patient', name=name)
    """
    if not name or not str(name).strip():
        return False, "Please provide a name to search", None
    return _profile_mgr._wrapper_search_patient_by_name(name)