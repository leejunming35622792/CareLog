from app.user import User

class PatientUser(User):
    def __init__(self, p_id, username, password, name, bday, gender, address, email, contact_num, date_joined, p_record, p_remark):
#assign unique ID for patients
        self.p_id = p_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)
        self.p_record = p_record or []
        self.p_remark = p_remark

#represents a single medical record entry for a patient
class PatientRecord():
    def __init__(self, pr_record_id, p_id, d_id, pr_timestamp, pr_conditions, pr_medications, pr_billings, pr_prediction_result, pr_confidence_score, pr_remark):
        self.pr_record_id = pr_record_id
        self.p_id = p_id
        self.d_id = d_id
        self.pr_timestamp = pr_timestamp
        self.pr_conditions = pr_conditions
        self.pr_medications = pr_medications
        self.pr_billings = pr_billings
        self.pr_prediction_result = pr_prediction_result
        self.pr_confidence_score = pr_confidence_score
        self.pr_remark = pr_remark
#represents an appointment between a patient and doctor
class PatientAppointment():
    def __init__(self, appt_id, p_id, d_id, appt_date, appt_time, appt_status, appt_remark):
        self.appt_id = appt_id
        self.p_id = p_id
        self.d_id = d_id
        self.date = appt_date
        self.time = appt_time
        self.status = appt_status
        self.remark = appt_remark

    @staticmethod
    def create(appt_id, p_id, d_id, appt_date, appt_time, appt_status, appt_remark):
        return PatientAppointment(appt_id, p_id, d_id, appt_date, appt_time, appt_status, appt_remark)
    
    @property
    def patient(self):
        return self.p_id

    @property
    def doctor(self):
        return self.d_id

    @property
    def appt_status(self):
        return self.status

    @property
    def appt_remark(self):
        return self.remark