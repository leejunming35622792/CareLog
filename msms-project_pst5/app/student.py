from app.user import User

class StudentUser(User):
    """Represents a student, inheriting from the base User class."""
    def __init__(self, user_id, name, username, password, instrument, enrolled_course_ids):
        super().__init__(user_id, name, username, password)
        self.instrument = instrument
        self.enrolled_course_ids = enrolled_course_ids or []


    def create_student_object(student_id, name, username, password, instrument, enrolled_courses):
        new_student = StudentUser(student_id, name, username, password, instrument, enrolled_courses)
        return new_student