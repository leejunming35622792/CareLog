from app.user import User

class NurseUser(User):
    def __init__(self, n_id, username, password, name, gender, address, email, contact_num, date_joined, speciality, department, with_doctor):
        self.n_id = n_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        self.speciality = speciality
        self.department = department 
        self.with_doctor = with_doctor  # store doctor ID
