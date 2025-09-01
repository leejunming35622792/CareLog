from app.user import User

class TeacherUser(User):
    """Represents a teacher."""
    # TODO: Implement the TeacherUser class, inheriting from User.
    # It should have an additional 'speciality' attribute in its __init__.
    
    def __init__(self, user_id, name, speciality):
        super().__init__(user_id, name)
        self.speciality = speciality

class Course:
    """Represents a single course offered by the school, linked to a teacher."""
    def __init__(self, course_id, name, instrument, teacher_id, enrolled_student_ids, lessons):
        self.id = course_id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.enrolled_student_ids = enrolled_student_ids or [] # To store multiple student IDs
        self.lessons = lessons or [] # To hold lesson dictionaries

