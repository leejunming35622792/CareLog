import json
from app.student import StudentUser
from app.teacher import TeacherUser, Course

# To control all business logic and data handling
class ScheduleManager:
    data_path="data/msms.json"

    # To hold objects
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []

        # create empty list for attendance log
        self.attendance_log = []

        # id counters
        self.next_student_id = 1
        self.next_teacher_id = 1

        # load existing data from msms.json
        self._load_data()

    # To load data from msms.json
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
    
    # To save data, instead of running _save_data()
    def save(self):
        self._save_data()

    # To convert object list to dictionary
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

    # Calling from main.py
    def enroll_student(self, name, courses):
        new_student = StudentUser(self.next_student_id, name, courses)
        # Save the new student into Student list
        self.students.append(new_student)
        print("--------------------")
        print(f"Student '{name}' with ID '{self.next_student_id}' is successfully registered for courses '{courses}'")
        print("--------------------")
        for student_course in courses:
            [c.enrolled_student_ids for c in self.courses if c.id == student_course][0].append(self.next_student_id)
            self.save()
        # Increase the next student ID by 1
        self.next_student_id += 1
    
    # Calling from main.py
    def enroll_teacher(self, name, speciality):
        new_teacher = TeacherUser(self.next_teacher_id, name, speciality)
        # Save the new student into Teacher list
        self.teachers.append(new_teacher)
        print("--------------------")
        print(f"Teacher '{name}' with ID '{self.next_teacher_id}' is successfully registered with speciality '{speciality}'")
        print("--------------------")
        # Increase the next teacher ID by 1
        self.next_teacher_id += 1

    # Calling from main.py
    # Save the new course into Courses list
    def add_course(self, course_id, course_name, course_instrument, teacher_id, enrolled_student_ids, lessons):
        new_course = Course(course_id, course_name, course_instrument, teacher_id, enrolled_student_ids, lessons)
        self.courses.append(new_course)
        print("--------------------")
        print(f"Course '{course_name}' with ID '{course_id}' is linked with Teacher ID '{teacher_id}' and instrument '{course_instrument}'")
        print("--------------------")

# Notes
# get() method returns the value of item with the specified key
# data.get("students", []) retuns a list under key "students" or [] if missing