import os
import datetime as dt
import app.utils as utils
from app.patient import PatientAppointment

# Roles we recognise
ROLES = {"patient", "doctor", "nurse", "receptionist", "admin"}

VALID_STATUSES = {"scheduled", "booked", "rescheduled", "cancelled", "completed", "no-show", "pending"}

class AppointmentManager:
    """
    Universal, role-aware helper for appointments.
    One class, one set of methods, permission-checked per call.
    Existing, role-specific wrappers (doctor/nurse/receptionist) can delegate to these.
    """

    def __init__(self, schedule_manager):
        self.sc = schedule_manager
        self.appointments = self.sc.appointments
        self.next_appt_id = self.sc.next_appt_id

    # ----------------------------- Public, role-aware API -----------------------------

    def create(self, actor_role, actor_username, patient_id, doctor_id, date, time, remark=""):
        """
        Create an appointment. Receptionist can create for any patient; patient can only create for themselves.
        Doctors/Nurses cannot create appointments (policy).
        """
        actor_role = (actor_role or "").lower()
        self._ensure_role(actor_role)
        self._ensure_user_exists(actor_username, actor_role)

        # Permission gate
        if actor_role not in {"receptionist", "patient", "admin"}:
            utils.log_event(f"Failed to create appointment: Role restricted", "ERROR")
            return False, "Only receptionists, patients or admins can create appointments.", None

        # Validate entities
        patient = self._get_patient(patient_id)
        doctor = self._get_doctor(doctor_id)
        if not patient:
            utils.log_event(f"Failed to create appointment: {patient_id} not found", "ERROR")
            return False, f"Patient ID '{patient_id}' not found.", None
        if not doctor:
            utils.log_event(f"Failed to create appointment: {doctor_id} not found", "ERROR")
            return False, f"Doctor ID '{doctor_id}' not found.", None

        # Patient can only book for self
        if actor_role == "patient":
            actor = self._get_user_by_username(actor_username, "patient")
            if not actor or getattr(actor, "p_id", None) != patient_id:
                utils.log_event(f"Failed to create appointment: Role restricted", "ERROR")
                return False, "Patients may only book appointments for themselves.", None

        # Build model
        appt_id = f"APPT{self.next_appt_id:04d}"
        new_appt = PatientAppointment(
            appt_id=appt_id,
            p_id=patient_id,
            d_id=doctor_id,
            appt_date=date,
            appt_time=time,
            appt_status="Pending",
            appt_remark=remark or ""
        )

        self.appointments.append(new_appt)
        self.next_appt_id += 1
        self.sc.next_appt_id = self.next_appt_id
        self.sc.save()

        utils.log_event(f"[{actor_role}] @{actor_username} created appointment {appt_id} (P={patient_id}, D={doctor_id})", "INFO")
        return True, f"Appointment {appt_id} created.", new_appt

    def update(self, manager, actor_role, actor_username, appt_id, *, date=None, time=None, doctor_id=None, status=None, remark=None):
        """
        Update parts of an appointment.
        - Receptionist/Admin: may change date/time/doctor/status/remark.
        - Patient: may reschedule/cancel only; cannot change doctor; cannot edit within <24h of the slot.
        - Doctor: may mark status-only (e.g., completed/no-show), cannot reschedule.
        - Nurse: status-only
        """
        
        actor_role = (actor_role or "").lower()
        self._ensure_role(actor_role)
        self._ensure_user_exists(actor_username, actor_role)

        found, msg, appt = self.sc.find_appointment_by_id(appt_id)
        if not found:
            utils.log_event(f"Failed to update appointment: Appointment not found", "ERROR")
            return False, msg, None

        # Compute current dt for policy checks
        appt_dt = self._parse_dt(appt.date, appt.time)

        # Receptionist/Admin: full control
        if actor_role in {"receptionist", "admin"}:
            pass  # allowed below

        elif actor_role == "patient":
            # May only affect own appointment and only reschedule/cancel with >= 24h notice
            actor = self._get_user_by_username(actor_username, "patient")
            if getattr(actor, "p_id", None) != appt.p_id:
                return False, "Patients may modify only their own appointments.", None

            if doctor_id is not None:
                return False, "Patients cannot change doctor.", None

            if appt_dt and (appt_dt - dt.datetime.now()).total_seconds() < 24 * 3600:
                return False, "Changes not allowed within 24 hours of the appointment.", None

            # status allowed only to 'cancelled'; reschedule via date/time
            if status is not None and status.lower() not in {"cancelled"}:
                return False, "Patients may only cancel their own appointments.", None

        elif actor_role == "doctor":
            # Doctors cannot reschedule; allow status-only update (completed/no-show)
            if any(v is not None for v in (date, time, doctor_id, remark)):
                return False, "Doctors cannot edit appointment schedule or remark.", None
            if status is None:
                return False, "Only status updates are allowed for doctors.", None
            if status.lower() not in {"completed", "no-show"}:
                return False, "Doctors may set status only to 'completed' or 'no-show'.", None

        elif actor_role == "nurse":
            if any(v is not None for v in (date, time, doctor_id, remark)):
                return False, "Doctors cannot edit appointment schedule or remark.", None
            if status is None:
                return False, "Only status updates are allowed for nurses.", None
            if status is not None and status.lower() not in {"scheduled", "cancelled", "completed", "no-show"}:
                return False, "Out of Nurse's work range.", None

        # Apply updates
        if date:
            appt.date = date
        if time:
            appt.time = time
        if doctor_id:
            doc = self._get_doctor(doctor_id)
            if not doc:
                return False, f"Doctor ID '{doctor_id}' not found.", None
            appt.d_id = doctor_id
        if status:
            if status.lower() not in VALID_STATUSES:
                return False, f"Invalid status '{status}'.", None
            appt.status = status.lower()
        if remark is not None:
            appt.remark = remark

        manager.save()
        self.sc.save()
        utils.log_event(f"[{actor_role}] {actor_username} updated appointment {appt_id}", "INFO")
        return True, f"Appointment {appt_id} updated.", appt

    def cancel(self, manager, actor_role, actor_username, appt_id):
        """Convenience: set status to 'cancelled' with permission checks."""
        return self.update(manager, actor_role, actor_username, appt_id, status="cancelled")

    def list(self, manager, actor_role, actor_username=None, *, scope="own", upcoming_only=False, date=None, status=None, patient_id=None, doctor_id=None, appt_id=None):
        actor_role = (actor_role or "").lower()
        self._ensure_role(actor_role)
        if actor_username:
            self._ensure_user_exists(actor_username, actor_role)

        now = dt.datetime.now()
        results = []

        # Determine default scope IDs
        doctor_self_id = patient_self_id = None
        if actor_role == "doctor":
            u = self._get_user_by_username(actor_username, "doctor")
            doctor_self_id = getattr(u, "d_id", None)
        elif actor_role == "patient":
            u = self._get_user_by_username(actor_username, "patient")
            patient_self_id = getattr(u, "p_id", None)

        for a in manager.appointments:
            # Scope filter
            if scope == "own":
                if actor_role == "doctor" and doctor_self_id and a.d_id != doctor_self_id:
                    continue
                if actor_role == "patient" and patient_self_id and a.p_id != patient_self_id:
                    continue
                # nurse / receptionist / admin -> see all in 'own' by default
            else:  # 'all'
                if actor_role in {"doctor", "patient", "nurse"}:
                    # clamp to own
                    if actor_role == "doctor" and doctor_self_id and a.d_id != doctor_self_id:
                        continue
                    if actor_role == "patient" and patient_self_id and a.p_id != patient_self_id:
                        continue

            # Explicit filters override scope
            if patient_id and a.p_id != patient_id:
                continue
            if doctor_id and a.d_id != doctor_id:
                continue

            # Parse dt
            a_dt = self._parse_dt(a.date, a.time)
            if upcoming_only and a_dt and a_dt < now:
                continue
            if date and a.date != date:
                continue
            if status and (a.status or "").lower() != status.lower():
                continue
            if appt_id and a.appt_id != appt_id:
                continue

            p = next((p for p in manager.patients if getattr(p, "p_id", None) == a.p_id), None)
            d = next((d for d in manager.doctors if getattr(d, "d_id", None) == a.d_id), None)

            results.append({
                "appt_id": a.appt_id,
                "patient_id": a.p_id,
                "patient_name": getattr(p, "name", "Unknown"),
                "doctor_id": a.d_id,
                "doctor_name": getattr(d, "name", "Unknown"),
                "date": a.date,
                "time": a.time,
                "status": a.status,
                "remark": a.remark,
                "_dt": a_dt or now
            })

        results.sort(key=lambda x: x["_dt"])
        for r in results:
            r.pop("_dt", None)
        return True, f"Found {len(results)} appointment(s).", results

    def export_report(self, actor_role, actor_username, appt_id):
        """
        Export a simple text report. Patients can export their own; doctor can export theirs;
        receptionist/admin can export any
        """
        from helper_manager.profile_manager import find_age
        actor_role = (actor_role or "").lower()

        ensure_role, msg, _ = self._ensure_role(actor_role)
        if not ensure_role:
            return False, msg, _
        
        ensure_user, msg, _ = self._ensure_user_exists(actor_username, actor_role)
        if not ensure_user:
            return False, msg, _

        found, msg, appt = self.sc.find_appointment_by_id(appt_id)
        if not found:
            return False, msg, None

        if actor_role in {"doctor", "patient"}:
            # Must belong to actor
            u = self._get_user_by_username(actor_username, actor_role)
            if actor_role == "doctor" and getattr(u, "d_id", None) != appt.d_id:
                return False, "You may export only your own appointments.", None
            if actor_role == "patient" and getattr(u, "p_id", None) != appt.p_id:
                return False, "You may export only your own appointments.", None
        elif actor_role == "nurse":
            return False, "Nurses cannot export appointment reports.", None

        patient = next((p for p in self.sc.patients if getattr(p, "p_id", None) == appt.p_id), None)
        doctor = next((d for d in self.sc.doctors if getattr(d, "d_id", None) == appt.d_id), None)

        # Build file
        folder_path = "appt_report"
        os.makedirs(folder_path, exist_ok=True)
        current_time = dt.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        file_dir = os.path.join(folder_path, f"{appt.appt_id}-{current_time}.txt")

        # Truncate remark
        remark = appt.remark or ""
        max_length = 37
        if len(remark) > max_length:
            remark = remark[: max_length - 4].rstrip() + " ..."

        # Write
        with open(file_dir, "w", encoding="utf-8") as f:
            f.write("+" + "=" * 70 + "+\n")
            f.write("|{:^70}|\n".format("CARELOG - APPOINTMENT REPORT"))
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Appointment ID", appt.appt_id))
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Patient ID:", getattr(patient, "p_id", "")))
            f.write("| {:25} {:<43}|\n".format("Patient Name:", getattr(patient, "name", "")))
            f.write("| {:25} {:<43}|\n".format("Patient Age:", find_age(getattr(patient, "bday", ""))))
            f.write("+" + " " * 70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Doctor:", getattr(doctor, "name", "")))
            f.write("| {:25} {:<43}|\n".format("Speciality", getattr(doctor, "speciality", "")))
            f.write("| {:25} {:<43}|\n".format("Department", getattr(doctor, "department", "")))
            f.write("+" + " " * 70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Date:", str(appt.date)))
            f.write("| {:25} {:<43}|\n".format("Time", str(appt.time)))
            f.write("+" + " " * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Remark", remark))
            f.write("+" + " " * 70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("+" + " " * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Status", appt.status))
            f.write("+" + " " * 70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")

        utils.log_event(f"[{actor_role}] {actor_username} exported report for {appt.appt_id}", "INFO")
        return True, "Report exported.", file_dir

    # ----------------------------- Legacy wrappers (optional) -----------------------------

    def view_all_appointments(self, manager, username):
        """Back-compat: doctor only; returns all (including past)."""
        ok, msg, rows = self.list(manager, "doctor", username, scope="own", upcoming_only=False)
        return ok, msg, rows

    def view_upcoming_appointments(self, manager, doctor_username):
        return self.list(manager, "doctor", doctor_username, scope="own", upcoming_only=True)

    def create_appointment_nurse(self, patient_id, doctor_id, date, time, remark):
        # Delegate to receptionist role since nurses cannot create by policy
        return self.create("nurse", "", patient_id, doctor_id, date, time, remark)

    def update_appointment_nurse(self, manager, appt_id, date=None, time=None, status=None, remark=None):
        return self.update(manager, "nurse", "", appt_id, date=date, time=time, status=status, remark=remark)

    def update_appointment_doctor(self, manager, username, appt_id, date=None, time=None, status=None, remark=None):
        return self.update(manager, "doctor", username, appt_id, date=date, time=time, status=status, remark=remark)

    # ----------------------------- Internals -----------------------------

    @staticmethod
    def _parse_dt(date_str, time_str):
        if not date_str or not time_str:
            return None
        src = f"{date_str} {time_str}".strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return dt.datetime.strptime(src, fmt)
            except ValueError:
                continue
        return None

    def _ensure_role(self, role):
        if role not in ROLES:
            return False, f"Unknown role '{role}'", None
        return True, "Role exists", None

    def _ensure_user_exists(self, username, role):
        if not username:
            return
        u = self._get_user_by_username(username, role)
        if not u:
            return False, f"User '{username}' with role '{role}' not found.", None
        return True, "User exists", None

    def _get_user_by_username(self, username, role):
        coll = {
            "patient": self.sc.patients,
            "doctor": self.sc.doctors,
            "nurse": self.sc.nurses,
            "receptionist": self.sc.receptionists,
            "admin": self.sc.admins,
        }[role]
        return next((u for u in coll if getattr(u, "username", None) == username), None)

    def _get_patient(self, p_id):
        return next((p for p in self.sc.patients if getattr(p, "p_id", None) == p_id), None)

    def _get_doctor(self, d_id):
        return next((d for d in self.sc.doctors if getattr(d, "d_id", None) == d_id), None)