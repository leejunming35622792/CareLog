from app.user import User

# To Create New Teacher
class TeacherUser(User):
    def __init__(self, username, password, user_id, name, speciality):
        super().__init__(username, password, user_id, name)
        self.speciality = speciality

# To Create New Course
class Course:
    def __init__(self, course_id, name, instrument, teacher_id, enrolled_student_ids, lessons):
        self.id = course_id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.enrolled_student_ids = enrolled_student_ids or []
        self.lessons = lessons or []

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