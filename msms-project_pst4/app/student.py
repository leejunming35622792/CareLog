from app.user import User

class StudentUser(User):
    def __init__(self, user_id, name, enrolled_course_ids):
        super().__init__(user_id, name)
        self.enrolled_course_ids = enrolled_course_ids or []