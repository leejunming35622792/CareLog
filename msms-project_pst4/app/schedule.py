import json
import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course, Lesson

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        # Create empty list to store objects
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []

        # Id counters
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_course_id = 1
        self.next_lesson_id = 1

        # Load existing data
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # Student object
                self.students = [StudentUser(s["id"], s["name"], s["enrolled_course_ids"]) for s in data.get("students",[])]

                # Teacher object
                self.teachers = [TeacherUser(t["id"], t["name"], t["speciality"]) for t in data.get("teachers", [])]

                # Course object
                self.courses = [Course(c["id"], c["name"], c["instrument"], c["teacher_id"], c["enrolled_student_ids"], c["lessons"]) for c in data.get("courses", [])]
                
                # Attendance object
                self.attendance_log = data.get("attendance", [])

                self.next_student_id = data.get("next_student_id", 1)
                self.next_teacher_id = data.get("next_teacher_id", 1)
                self.next_course_id = data.get("next_course_id", 1)
                self.next_lesson_id = data.get("next_lesson_id", 1)
                
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
            "next_course_id": self.next_course_id,
            "next_lesson_id": self.next_lesson_id
        }
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)    

    def save(self):
        self._save_data()

    def check_num(input):
        if not input.isalpha:
            return False
        return True
    
    def check_str(input):
        if not input.isalpha:
            return False
        return True

    def enrolment(self, reg_name, reg_instrument, reg_course):
        if reg_course != None:
            # Create new object
            new_student = StudentUser(self.next_student_id, reg_name, reg_course)

            # Add Student ID to each Course
            for c in self.courses:
                if c.id in reg_course:
                    c.enrolled_student_ids.append(self.next_student_id)

            # Add to Students Dataset
            self.students.append(new_student)

            # Increase next student ID
            self.next_student_id += 1

            return True
        else:
            # Create new object
            new_teacher = TeacherUser(self.next_teacher_id, reg_name, reg_instrument)

            # Add to Teachers Dataset
            self.teachers.append(new_teacher)

            # Increase next teacher ID
            self.next_teacher_id += 1

            return True
        return False
        
    def update_student(self, update_id, update_name, update_course):
        # Update the particular student info
        for s in self.students:
            if str(s.id) == str(update_id):
                s.name = update_name
                s.enrolled_course_ids = update_course.sort()
                
        # Update enrolled student ids
        for c in self.courses:
            if c.id in update_course and int(update_id) not in c.enrolled_student_ids: 
                c.enrolled_student_ids.append(int(update_id))
            if int(update_id) in c.enrolled_student_ids and c.id not in update_course:
                c.enrolled_student_ids.remove(int(update_id))
        return True

    def update_teacher(self, update_id, update_name, update_speciality):
        for t in self.teachers:
            if str(t.id) == update_id:
                t.name = update_name
                t.speciality = update_speciality
                return True
            return False
        
    def search_student(self, s_id):
        # Find all student IDs
        all_student_ids = [s.id for s in self.students]

        if len(s_id.strip()) != 0:
            if s_id.strip() in map(str, all_student_ids):

                s_id = str(s_id)

                student = next((s for s in self.students if str(s.id)== s_id), None)

                if not student:
                    return None
                
                student_info_dict = [{
                    "Student ID": student.id,
                    "Student Name": student.name,
                    "Courses": student.enrolled_course_ids
                }]
                
                return student_info_dict
            return False
        return False
            
    def print_card(self, s_id):

        s_id = str(s_id)

        find_student = next((s for s in self.students if str(s.id) == s_id), None)

        if find_student:
            filename = f"{s_id}_card.txt"

            with open(filename, "w") as f:
                f.write("========================\n")
                f.write(f"  MUSIC SCHOOL ID BADGE\n")
                f.write("========================\n")
                f.write("ID            : ".ljust(16) + f"{find_student.id}\n")
                f.write("Name          :".ljust(16) + f"{find_student.name}\n")
                f.write("Course Joined : ".ljust(16) + f"{find_student.enrolled_course_ids}\n")
            return filename
        else:
            return False
        
    def add_course(self, new_course_name, new_course_instrument, new_course_teacher_id):
        new_course = Course(self.next_course_id,new_course_name, new_course_instrument, new_course_teacher_id, [], [])

        self.courses.append(new_course)
        self.next_course_id += 1

        return True
    
    def add_lesson(self, course_lesson, lesson_day, lesson_start_time, lesson_room, lesson_remark):
        new_lesson = Lesson(self.next_lesson_id, lesson_day, str(lesson_start_time), lesson_room, lesson_remark)

        for c in self.courses:
            if c.id == int(course_lesson):
                c.lessons.append(new_lesson.to_dict())
                self.next_lesson_id += 1
                return True
        return False

    def check_in(self, student_id, course_id, timestamp=None):
        # Get current datetime
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create attendance object
        check_in_record = {
            "student_id": int(student_id),
            "course_id": course_id,
            "timestamp": timestamp
        }

        # Add into attendance log
        self.attendance_log.append(check_in_record)
        return True
