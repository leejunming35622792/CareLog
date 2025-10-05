import json, re
from app.user import User
import app.utils as utils

class ReceptionistUser(User):
    def __init__(self, r_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.r_id = r_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)

    def create_user(self, role, username, password, user_id, date):
        return super().create_user(role, username, password, user_id, date)
    
    def create_appointment(self, patient_id, doctor_id, date, time):
        from app.schedule import ScheduleManager as sc

        # Validate ID
        patient = next((p for p in sc.patients if p.p_id == patient_id), None)
        doctor = next((d for d in sc.doctors if d.d_id == doctor_id), None)

        if not patient or not doctor:
            utils.log_event(f"Invalid patient or doctor ID for appointment ({patient_id}, {doctor_id})", "ERROR")
            return False, "Invalid patient or doctor ID", None
        
        appt_id = f"A{sc.next_appt_id:04d}"
        appointment = {
            "appt_id": appt_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "status": "Scheduled",
            "created_by": self.username,
        }
        sc.appointments.append(appointment)
        sc.next_appt_id += 1
        sc.save()

        utils.log_event(f"Appointment {appt_id} created by receptionist {self.username}", "INFO")
        return True, f"Appointment {appt_id} successfully created.", appointment
    
    def view_appointments(self):
        from app.schedule import ScheduleManager as sc
        return sc.appointments
    
    def update_appointment_status(self, appt_id, new_status):
        from app.schedule import ScheduleManager as sc

        appointment = next((a for a in sc.appointments if a["appt_id"] == appt_id), None)
        if not appointment:
            return False, "Appointment not found"

        appointment["status"] = new_status
        sc.save()
        utils.log_event(f"Appointment {appt_id} status updated to {new_status}", "INFO")
        return True, f"Appointment {appt_id} updated successfully"
    
    def cancel_appointment(self, appt_id):
        return self.update_appointment_status(appt_id, "Cancelled")

    """ Patient and Doctor Info """
    def list_patients(self):
        from app.schedule import ScheduleManager as sc
        return [(p.p_id, p.name, p.contact_num) for p in sc.patients]

    def list_doctors(self):
        from app.schedule import ScheduleManager as sc
        return [(d.d_id, d.name, d.contact_num) for d in sc.doctors]
    
    def list_nurses(self):
        from app.schedule import ScheduleManager as sc
        return [(n.n_id, n.name, n.contact_num) for n in sc.nurses]