from app.user import User

# To create a class for Student
class StudentUser(User):
    def __init__(self, user_id, name, enrolled_course_ids):
        # To Call the parent class's __init__ method using super().
        super().__init__(user_id, name)
        self.enrolled_course_ids = enrolled_course_ids