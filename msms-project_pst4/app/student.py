from app.user import User

class StudentUser(User):
    def __init__(self, username, password, user_id, name, instrument, enrolled_course_ids):
        super().__init__(username, password, user_id, name)
        self.instrument = instrument
        self.enrolled_course_ids = enrolled_course_ids or []