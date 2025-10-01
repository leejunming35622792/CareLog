import datetime

from app.user import User

class PatientUser(User):
    def __init__(self, p_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.p_id = p_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        self.p_record = []

class PatientRecord():
    def __init__(self, pr_record_id, p_id, pr_conditions, pr_prediction_result, pr_confidence_score):
        self.pr_record_id = pr_record_id
        self.patient = p_id
        self.pr_timestamp = datetime.datetime.now()
        self.pr_conditions = pr_conditions
        self.pr_prediction_result = pr_prediction_result
        self.pr_confidence_score = pr_confidence_score

# TODO: appointments
# TODO: class PatientCondition():
#     def __init__(self, name, severity, notes):
#         self.name = name
#         self.severity = severity
#         self.notes = notes