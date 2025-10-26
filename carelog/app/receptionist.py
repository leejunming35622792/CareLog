import re
from app.user import User
import app.utils as utils
from app.patient import PatientAppointment
from helper_manager.appointment_manager import AppointmentManager

class ReceptionistUser(User):
    def __init__(self, r_id, username, password, name, bday, gender, address, email, contact_num, date_joined):
        self.r_id = r_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)

    # Account creation (Patients only)
    def create_user(self, role, username, password, user_id, date):
        return super().create_user(role, username, password, user_id, date)
    
    def create_appointment(self, manager, patient_id, doctor_id, appt_date, appt_time, remark=""):
        # Validate ID
        patient = next((p for p in manager.patients if p.p_id == patient_id), None)
        doctor = next((d for d in manager.doctors if d.d_id == doctor_id), None)

        if not patient or not doctor:
            utils.log_event(f"Invalid patient or doctor ID for appointment ({patient_id}, {doctor_id})", "ERROR")
            return False, "Invalid patient or doctor ID", None
        
        appt_id = manager.next_appt_id if isinstance(manager.next_appt_id, str) else f"A{manager.next_appt_id:04d}"
        new_appointment = PatientAppointment.create(
            appt_id, patient_id, doctor_id, appt_date, appt_time, "scheduled", remark or ""
        )
        manager.appointments.append(new_appointment)
        manager.next_appt_id += 1
        manager.save()

        utils.log_event(f"Appointment {appt_id} created by receptionist {self.username}", "INFO")
        return True, f"Appointment {appt_id} successfully created.", new_appointment
    
    def view_appointments(self, manager):
        return manager.appointments
    
    def update_appointment_status(self, manager, username, appt_id, new_status):
        AppointmentManager.update(manager, "receptionist", username, appt_id, date=None, time=None, doctor_id=None, status=new_status, remark=None)
        manager.save()
        utils.log_event(f"Appointment {appt_id} status updated to {new_status}", "INFO")
        return True, f"Appointment {appt_id} updated successfully"
    
    def cancel_appointment(self, appt_id):
        return self.update_appointment_status(appt_id, "Cancelled")

    """ Patient and Doctor Info """
    def list_patients(self):
        from app.schedule import ScheduleManager
        return [(p.p_id, p.name, p.contact_num) for p in ScheduleManager.patients]

    def list_doctors(self):
        from app.schedule import ScheduleManager
        return [(d.d_id, d.name, d.contact_num) for d in ScheduleManager.doctors]
    
    def list_nurses(self):
        from app.schedule import ScheduleManager
        return [(n.n_id, n.name, n.contact_num) for n in ScheduleManager.nurses]
    
    """Search for patient"""
    def search_patients(self, query, manager):
        q = (query or "").lower()
        return [
            p for p in manager.patients
            if q in (p.name or "").lower()
            or q in (p.p_id or "").lower()
            or q in (p.email or "").lower()
            or q in (p.contact_num or "").lower()
        ]