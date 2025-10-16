import datetime
from app.patient import PatientAppointment
import app.utils as utils

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
        """Return upcoming appointments for a specific doctor"""
        doctor = next((d for d in self.sc.doctors if d.username == doctor_username), None)
        if not doctor:
            return False, "No Doctor Found", []

        now = datetime.datetime.now()
        upcoming = []

        for appt in self.appointments:
            if appt.d_id == doctor.d_id:
                try:
                    appt_dt = datetime.datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
                    if appt_dt >= now:
                        patient = next((p for p in self.sc.patients if p.p_id == appt.p_id), None)
                        upcoming.append({
                            "appt_id": appt.appt_id,
                            "patient_id": appt.p_id,
                            "patient_name": patient.name if patient else "Unknown",
                            "date": appt.date,
                            "time": appt.time,
                            "status": appt.status,
                            "remark": appt.remark,
                        })
                except ValueError:
                    continue

        upcoming.sort(key=lambda x: f"{x['date']} {x['time']}")
        return True, f"Found {len(upcoming)} upcoming appointments", upcoming