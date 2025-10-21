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
    
    def view_all_appointments(self, username):
        """Return all appointments"""
        user = next((d for d in self.sc.doctors if getattr(d, "username", None) == username), None)
        
        if not user:
            return False, f"{user} not found", []
        
        user_id = getattr(user, f"d_id", None)
        if not user_id:
            return False, f"{user} record missing {user_id}, []"
        
        appointment = []

        for appt in self.appointments:
            a_did  = getattr(appt, "d_id", None)
            a_pid  = getattr(appt, "p_id", None)
            a_date = getattr(appt, "date", None)
            a_time = getattr(appt, "time", None)

            if a_did != user_id or not (a_pid and a_date and a_time):
                continue

            appt_dt = self._parse_dt(a_date, a_time)
            if appt_dt is None:
                # date/time not in an accepted format; skip
                continue
            
            patient = next((p for p in self.sc.patients if getattr(p, "p_id", None) == a_pid), None)
            p_name = getattr(patient, "name", "Unknown")

            appointment.append({
                "appt_id": getattr(appt, "appt_id", None),
                "patient_id": a_pid,
                "patient_name": p_name,
                "date": a_date,
                "time": a_time,
                "status": getattr(appt, "status", "Pending"),
                "remark": getattr(appt, "remark", ""),
                "_dt": appt_dt
            })

        # Sort by actual datetime
        appointment.sort(key=lambda x: x["_dt"])
        for item in appointment:
            item.pop("_dt", None)
        return True, f"Found {len(appointment)} upcoming appointment(s)", appointment

    def view_upcoming_appointments(self, doctor_username):
        """Return upcoming (>= now) appointments for a specific doctor."""
        # Find the doctor by username
        doctor = next((d for d in self.sc.doctors if d.username == doctor_username), None)

        # If no doctor found
        if not doctor:
            return False, "No Doctor Found", []

        # Error handling - if ID missing
        doctor_id = getattr(doctor, "d_id", None)
        if not doctor_id:
            return False, "Doctor record missing d_id", []

        # Get current datetime
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

            # Convert to datetime
            appt_dt = self._parse_dt(a_date, a_time)
            if appt_dt is None:
                continue  # Skip invalid date/time

            if appt_dt < now:
                continue  # Skip past appointments

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
                "_dt": appt_dt  # store temporarily for sorting
            })

        # Sort by datetime
        upcoming.sort(key=lambda x: x["_dt"])

        # Remove the temporary key
        for item in upcoming:
            item.pop("_dt", None)

        return True, f"Found {len(upcoming)} upcoming appointment(s)", upcoming

    def create_appointment_nurse(self, patient_id, doctor_id, date, time, remark):
        """Create a new appointment"""
        found_p, msg_p, patient = self.sc.find_patient_by_id(patient_id)
        if not found_p:
            return False, msg_p, None

        found_d, msg_d, doctor = self.sc.find_doctor_by_id(doctor_id)
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
        self.sc.save()

        return True, f"Appointment {appt_id} created successfully", new_appointment

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
    
    def view_appointment_nurse(self, appointment_id=None, patient_id=None):
        """View appointments - all, by ID, or by patient"""
        if appointment_id:
            found, msg, appt = self.sc.find_appointment_by_id(appointment_id)
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
        found, msg, appt = self.sc.find_appointment_by_id(appt_id)
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
        self.sc.save()

        return True, f"Appointment {appt_id} updated successfully", appt

    def delete_appointment_nurse(self, appointment_id):
        """Cancel/delete appointment"""
        found, msg, appt = self.sc.find_appointment_by_id(appointment_id)
        if not found:
            return False, msg, None

        
        appt.status = "cancelled"
        self.sc.save()
        
        utils.log_event(f"Nurse cancelled appointment {appointment_id}", "INFO")
        return True, "Appointment cancelled successfully", appointment_id
    
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