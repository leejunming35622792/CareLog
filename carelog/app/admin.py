from app.user import User

class AdminUser(User):
    def __init__(self, a_id, username, password, name, gender, address, email, contact_num, date_joined):
        self.a_id = a_id
        super().__init__(username, password, name, gender, address, email, contact_num, date_joined)
        