import json
from app.student import StudentUser
from app.teacher import TeacherUser, Course

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []

        # Create empty list for attendance log
        self.attendance_log = []

        # Id counters
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_lesson_id = 1

        # Load existing data
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # Student object
                self.students = [StudentUser(s["id"], s["name"], s.get("enrolled_course_ids",[])) for s in data.get("students",[])]

                # Teacher object
                self.teachers = [TeacherUser(t["id"], t["name"], t["speciality"]) for t in data.get("teachers", [])]

                # Course object
                self.courses = [Course(c["id"], c["name"], c["instrument"], c["teacher_id"], c["enrolled_student_ids"], c["lessons"]) for c in data.get("courses", [])]
                
                # Attendance object
                self.attendance_log = data.get("attendance", [])

                self.next_student_id = data.get("next_student_id", "1")
                self.next_teacher_id = data.get("next_teacher_id", "1")
                
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
    
    def _save_data(self):
        # To create a 'data_to_save' dictionary.
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log,
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
        }
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)    

    def save(self):
        self._save_data()

    def register_new_student(self, reg_name, reg_instrument):
        # Create new object
        new_student = StudentUser(reg_name, reg_instrument)
        # Add to Students Dataset
        self.students.append(new_student)
        # Increase next student ID
        self.next_student_id += 1