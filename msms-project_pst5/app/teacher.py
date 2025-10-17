from app.user import User

class TeacherUser(User):
    """Represents a teacher."""
    def __init__(self, user_id, name, username, password, speciality):
        super().__init__(user_id, name, username, password)
        self.speciality = speciality

    @staticmethod
    def create_teacher_object(teacher_id, name, username, password, speciality):
        new_teacher = TeacherUser(teacher_id, name, username, password, speciality)
        return new_teacher

class Course:
    """Represents a single course offered by the school, linked to a teacher."""
    def __init__(self, course_id, name, instrument, teacher_id, enrolled_student_ids, lessons):
        self.id = course_id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.enrolled_student_ids = enrolled_student_ids or []
        self.lessons = lessons or []

    @staticmethod
    def create_course_object(course_id, name, instrument, teacher_id):
        new_course = Course(course_id, name, instrument, teacher_id)
        return new_course

# To Create New Lesson
class Lesson:
    def __init__(self, lesson_id, lesson_day, lesson_start_time, lesson_room, remark):
        self.lesson_id = lesson_id
        self.lesson_day = lesson_day
        self.lesson_start_time = lesson_start_time
        self.lesson_room = lesson_room
        self.lesson_remark = remark

    def to_dict(self):
        return {
            "lesson-id": self.lesson_id,
            "day": self.lesson_day,
            "start_time": self.lesson_start_time,
            "room": self.lesson_room,
            "remark": self.lesson_remark
        }
    
    @staticmethod
    def create_lesson_object(lesson_id, lesson_day, lesson_time, lesson_room, lesson_remark):
        new_lesson = Lesson(lesson_id, lesson_day, lesson_time, lesson_room, lesson_remark)
        return new_lesson
    

