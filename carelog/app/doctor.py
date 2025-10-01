from app.user import User

class DoctorUser(User):
    def __init__(self, d_id, username, password, name, gender, address, email, contact_num, date_joined, speciality, department):
        self.d_id = d_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        self.speciality = speciality
        self.department = department
        