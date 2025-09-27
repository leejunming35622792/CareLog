import json
import os
import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course, Lesson
from app.staff import StaffUser

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        # Create empty list to store objects
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.staff = []
        self.courses = []
        self.attendance_log = []

        # Id counters
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_staff_id = 1
        self.next_course_id = 1
        self.next_lesson_id = 1

        # Load existing data
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # Student object
                self.students = [StudentUser(s["username"], s["password"], s["id"], s["name"], s["instrument"], s["enrolled_course_ids"]) for s in data.get("students",[])]

                # Teacher object
                self.teachers = [TeacherUser(t["username"], t["password"], t["id"], t["name"], t["speciality"]) for t in data.get("teachers", [])]

                # Staff object
                self.staff = [StaffUser(u["username"], u["password"]) for u in data.get("staff", [])]

                # Course object 
                self.courses = [Course(c["id"], c["name"], c["instrument"], c["teacher_id"], c["enrolled_student_ids"], c["lessons"]) for c in data.get("courses", [])]
                
                # Attendance object
                self.attendance_log = data.get("attendance", [])

                # IDs
                self.next_student_id = data.get("next_student_id", 1)
                self.next_teacher_id = data.get("next_teacher_id", 1)
                self.next_staff_id = data.get("next_staff_id", 1)
                self.next_course_id = data.get("next_course_id", 1)
                self.next_lesson_id = data.get("next_lesson_id", 1)
                
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")         
    
    def _save_data(self):
        # To create a 'data_to_save' dictionary.
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "staff": [u.__dict__ for u in self.staff],
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

    def load_json(file_path, default_data):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if not os.path.exists(file_path):
            # Ensure parent folder exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Use {} if no default data is provided
            if default_data is None:
                default_data = {}

            # Write the default JSON
            with open(file_path, "w") as f:
                json.dump(default_data, f, indent=4)

            return default_data

    def check_num(input):
        if not input.isalpha:
            return False
        return True
    
    def check_str(input):
        if not input.isalpha:
            return False
        return True

    # --------- Create --------- 
    def enrolment(self, staff, username, password, reg_name, reg_instrument, reg_course):
        if reg_name == None:
            reg_name = ""

        if reg_instrument == None:
            reg_instrument = ""

        if staff == "s":
            # Sort course ID
            if not reg_course:
                reg_course = []
            else:
                reg_course.sort()
                for c in self.courses:
                    if c.id in reg_course:
                        c.enrolled_student_ids.append(self.next_student_id)

            # Create new object
            new_student = StudentUser(username, password, self.next_student_id, reg_name, reg_instrument, reg_course)

            # Add to Students Dataset
            self.students.append(new_student)

            # Increase next student ID
            self.next_student_id += 1

            return True
        elif staff == "t":
            # Create new object
            new_teacher = TeacherUser(username, password, self.next_teacher_id, reg_name, reg_instrument)

            # Add to Teachers Dataset
            self.teachers.append(new_teacher)

            # Increase next teacher ID
            self.next_teacher_id += 1

            return True
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
    # --------------------------

    # --------- Update --------- 
    def update_student(self, username, password, update_id, update_name, update_instrument, update_course):
        # Prevent null
        if update_course is None:
            update_course = []

        # Update the particular student info
        for s in self.students:
            if str(s.id) == str(update_id) or s.username == username:
                if not update_id:
                    update_id = s.id
                if username:
                    s.username = username
                if password:
                    s.password = password
                if update_name:
                    s.name = update_name
                if update_instrument:
                    s.intrument = update_instrument
                if update_course:
                    s.enrolled_course_ids = sorted(update_course)
                
        # Update enrolled student ids
        for c in self.courses:
            if c.id in update_course and int(update_id) not in c.enrolled_student_ids: 
                c.enrolled_student_ids.append(int(update_id))
            if int(update_id) in c.enrolled_student_ids and c.id not in update_course:
                c.enrolled_student_ids.remove(int(update_id))
                
        return True

    def update_teacher(self, username, password, update_id, update_name, update_speciality):
        for t in self.teachers:
            if str(t.id) == str(update_id) or t.username == username:
                if not update_id:
                    update_id = t.id 
                if username:
                    t.username = username
                if password:
                    t.password = password
                if update_name:
                    t.name = update_name
                if update_speciality:
                    t.speciality = update_speciality
                return True
        return False
        
    def update_course(self, update_course_id, update_name, update_instrument, update_teacher):
        for c in self.courses:
            if str(c.id) == str(update_course_id):
                if update_name:
                    c.name = update_name
                if update_instrument:
                    c.instrument = update_instrument
                if update_teacher:
                    c.teacher_id = update_teacher
                return True 
        return False

    def update_lesson(self, update_lessonID, update_day, update_starttime, update_room, update_remark):
        for c in self.courses:
                for l in c.lessons:
                    if str(l["lesson-id"]) == str(update_lessonID):
                        if update_day:
                            l["day"] = update_day
                        if update_starttime:
                            l["start_time"] = str(update_starttime)
                        if update_room:
                            l["room"] = update_room
                        if update_remark:
                            l["remark"] = update_remark
                        return True
        return False
    # --------------------------

    # --------- Delete --------- 
    def remove_student(self, s_id):
        student = next((s for s in self.students if str(s.id) == str(s_id)), None)

        if student:
            self.students.remove(student)
            return True
        else:
            return False

    def remove_teacher(self, t_id):
        self.teachers = [t for t in self.teachers if str(t.id) != str(t_id)]
        return True

    def delete_course(self, delete_course_id):
        self.courses = [c for c in self.courses if str(c.id) != str(delete_course_id)]
        return True
    
    def delete_lesson(self, delete_lessonID):
        new_lessons = []
        for c in self.courses:
            c.lessons = [l for l in c.lessons if l["lesson-id"] != delete_lessonID]
            return True
    # --------------------------

    # --------- Read/ Other Feature --------- 
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
    
    def search_function(self, staff, search_keyword):
        # Search Student
        if staff == "S":
            # Create empty list to store data
            match_student = []
            
            for s in self.students:
                s_name = s.name
                if search_keyword.lower() in s_name.lower():
                    match_student.append({
                        "Student ID": s.id,
                        "Student Name": s.name,
                        "Courses Enrolled": s.enrolled_course_ids
                    })

            return match_student
        
        # Search Teacher
        if staff == "T":
            # Create empty list to store data
            match_teacher = []
            
            # Search by 
            for t in self.teachers:
                if search_keyword.lower() in t.name.lower():
                    match_teacher.append({
                        "Teacher ID": t.id,
                        "Teacher Name": t.name,
                        "Speciality": t.speciality
                    })

            return match_teacher


        
