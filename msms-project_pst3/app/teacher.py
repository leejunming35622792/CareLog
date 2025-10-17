from app.user import User

# To create a class for Teacher
class TeacherUser(User):    
    def __init__(self, user_id, name, speciality):
        # To Call the parent class's __init__ method using super().
        super().__init__(user_id, name)
        self.speciality = speciality

# To create a class for Course
class Course:
    def __init__(self, course_id, name, instrument, teacher_id, enrolled_student_ids, lessons):
        self.id = course_id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.enrolled_student_ids = enrolled_student_ids or [] # To store multiple student IDs
        self.lessons = lessons or [] # To hold lesson dictionaries
