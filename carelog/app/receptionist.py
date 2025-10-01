from app.user import User

class ReceptionistUser(User):
    def __init__(self, r_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.r_id = r_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
