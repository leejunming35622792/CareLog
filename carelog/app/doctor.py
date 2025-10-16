from app.user import User

class DoctorUser(User):
    def __init__(self, d_id: int, username: str, password: str, name: str, gender: str,
                 address: str, email: str, contact_num: str, date_joined: str, speciality: str, department: str):
        
        self.d_id = d_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        self.speciality = speciality
        self.department = department

    def __str__(self) -> str:
        return f"Doctor {self.name} ({self.speciality}, {self.department})"
