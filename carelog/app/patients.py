from app.user import User

class PatientUser(User):
    def __init__(self, username, password):
        super().__init__(username, password)
