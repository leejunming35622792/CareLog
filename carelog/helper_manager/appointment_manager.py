import os
import datetime
import app.utils as utils
from app.patient import PatientAppointment
from helper_manager.profile_manager import find_age

class AppointmentManager:
    def __init__(self, schedule_manager):
        """
        Manage all appointments.
        schedule_manager: instance of ScheduleManager
        """
        self.sc = schedule_manager
        self.appointments = self.sc.appointments
        self.next_appt_id = self.sc.next_appt_id

    def add_appointments(self, p_id, d_id, appt_date, appt_time, appt_remark):
        # Get next appointment id
        appt_id = f"AAPT{self.next_appt_id:04d}"

        # Validation
        if not all([p_id, d_id, appt_date, appt_time]):
            utils.log_event("Appointment creation failed: Missing details", "ERROR")
            return False, "All details required"
        
        # Ensure valid patient/doctor
        patient = next((p for p in self.sc.patients if p.p_id == p_id), None)
        doctor = next((d for d in self.sc.doctors if d.d_id == d_id), None)
        if not patient:
            return False, f"Patient ID '{p_id}' not found"
        if not doctor:
            return False, f"Doctor ID '{d_id}' not found"

        # Create appointment
        new_appt = PatientAppointment.create(appt_id, p_id, d_id, appt_date, appt_time, "Pending", appt_remark)
        
        self.appointments.append(new_appt)
        self.next_appt_id += 1
        self.sc.next_appt_id = self.next_appt_id
        self.sc.save()

        utils.log_event(f"Appointment {appt_id} created for patient {p_id} with doctor {d_id}", "INFO")
        return True, f"Appointment {appt_id} created successfully"
    
    def edit_appointments(self, appt_id, d_id, appt_date, appt_time, appt_remark):
        """Edit existing appointment"""
        appt = next((a for a in self.appointments if a.appt_id == appt_id), None)
        if not appt:
            return False, f"Appointment {appt_id} not found"
        if d_id:
            appt.d_id = d_id
        if appt_date:
            appt.date = appt_date
        if appt_time:
            appt.time = appt_time
        if appt_remark:
            appt.remark = appt_remark

        self.sc.save()
        utils.log_event(f"Appointment {appt_id} updated", "INFO")
        return True, f"Appointment {appt_id} updated successfully"

    def delete_appointments(self, appt_id):
        """Delete an appointment by ID"""
        initial_len = len(self.appointments)
        self.appointments = [a for a in self.appointments if a.appt_id != appt_id]
        self.sc.appointments = self.appointments

        if len(self.appointments) < initial_len:
            self.sc.save()
            utils.log_event(f"Appointment {appt_id} deleted", "INFO")
            return True, f"Appointment {appt_id} deleted"
        else:
            return False, f"No appointment with ID {appt_id}"

    def search_appt(self, appt_id):
        """Find appointment details by ID"""
        appt = next((a for a in self.appointments if a.appt_id == appt_id), None)
        if not appt:
            return False, f"No appointment found with ID {appt_id}"

        result = {
            "Appointment ID": appt.appt_id,
            "Patient ID": appt.p_id,
            "Doctor ID": appt.d_id,
            "Appointment Date": appt.date,
            "Appointment Time": appt.time,
            "Appointment Status": appt.status,
            "Remark": appt.remark,
        }
        return True, "Appointment found", result
    
    def view_upcoming_appointments(self, doctor_username):
        """Return upcoming (>= now) appointments for a specific doctor."""
        # Find the doctor by username
        doctor = next((d for d in self.sc.doctors if getattr(d, "username", None) == doctor_username), None)
        if not doctor:
            return False, "No Doctor Found", []

        doctor_id = getattr(doctor, "d_id", None)
        if not doctor_id:
            return False, "Doctor record missing d_id", []

        now = datetime.datetime.now()
        upcoming = []

        for appt in self.appointments:
            a_did  = getattr(appt, "d_id", None)
            a_pid  = getattr(appt, "p_id", None)
            a_date = getattr(appt, "date", None)
            a_time = getattr(appt, "time", None)

        # Only this doctor's appointments, with basic fields present
            if a_did != doctor_id or not (a_pid and a_date and a_time):
                continue

            appt_dt = self._parse_dt(a_date, a_time)
            if appt_dt is None:
                # date/time not in an accepted format; skip
                continue

            # Keep only future (>= now)
            if appt_dt < now:
                continue

            patient = next((p for p in self.sc.patients if getattr(p, "p_id", None) == a_pid), None)
            p_name = getattr(patient, "name", "Unknown")

            upcoming.append({
                "appt_id": getattr(appt, "appt_id", None),
                "patient_id": a_pid,
                "patient_name": p_name,
                "date": a_date,
                "time": a_time,
                "status": getattr(appt, "status", "Pending"),
                "remark": getattr(appt, "remark", ""),
            })

        # Sort by actual datetime
        upcoming.sort(key=lambda x: x["_dt"])
        for item in upcoming:
            item.pop("_dt", None)
        return True, f"Found {len(upcoming)} upcoming appointment(s)", upcoming

    # helper: parse "YYYY-MM-DD" + "HH:MM[:SS]"
    @staticmethod
    def _parse_dt(date_str, time_str):
        """Parse 'YYYY-MM-DD' + 'HH:MM[:SS]' into a datetime, or return None if invalid."""
        if not date_str or not time_str:
            return None
        src = f"{date_str} {time_str}".strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.datetime.strptime(src, fmt)
            except ValueError:
                continue
        return None
    

    def print_appt(self, patient, appt):
        # Find current patient detail
        current_patient = next((p for p in self.sc.patients if p.username == patient.username))
        current_doctor = next((d for d in self.sc.doctors if d.d_id == appt["Doctor ID"]))

        # Folder directory stores appointment report
        folder_path = "appt_report"
        # Make sure dir exists
        os.makedirs(folder_path, exist_ok=True)
        # Create text file
        file_dir = os.path.join(folder_path, f"{appt["Doctor ID"]}.txt")

        # Set limit to remark
        remark = appt["Remark"]
        max_length = 37

        if len(remark) > max_length:
            remark = remark[:max_length - 4].rstrip() + " ..."

        # Create message
        with open(file_dir, "w", encoding="utf-8") as f:
            f.write("+" + "="*70 + "+\n")
            f.write("|{:^70}|\n".format("CARELOG - APPOINTMENT REPORT"))
            f.write("+" + "="*70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Appointment ID", appt["Doctor ID"]))
            f.write("+" + "="*70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Patient ID:", patient.p_id))
            f.write("| {:25} {:<43}|\n".format("Patient Name:", patient.name))
            f.write("| {:25} {:<43}|\n".format("Patient Age:", find_age(patient.bday)))
            f.write("+" + " "*70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Doctor:", current_doctor.name))
            f.write("| {:25} {:<43}|\n".format("Speciality", current_doctor.speciality))
            f.write("| {:25} {:<43}|\n".format("Department", current_doctor.department))
            f.write("+" + " "*70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Date:", str(appt["Appointment Date"])))
            f.write("| {:25} {:<43}|\n".format("Time", str(appt["Appointment Time"])))
            f.write("+" + " "*70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Remark", remark))
            f.write("+" + " "*70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("+" + " "*70 + "+\n")
            f.write("| {:25} {:<43}|\n".format("Status", appt["Appointment Status"]))
            f.write("+" + " "*70 + "+\n")
            f.write("+" + "=" * 70 + "+\n")
        return file_dir

