from app.user import User
# the doctor user class inheriting from the base user class
class DoctorUser(User):
    def __init__(self, d_id: int, username: str, password: str, name: str, bday: int, gender: str,
                 address: str, email: str, contact_num: str, date_joined: str, speciality: str, department: str):
        
        self.d_id = d_id
        super().__init__(username, password, name, bday, gender, address, email, contact_num, date_joined)
        self.speciality = speciality
        self.department = department
# string representation of the doctor user
    def __str__(self) -> str:
        return f"Doctor {self.name} ({self.speciality}, {self.department})"
