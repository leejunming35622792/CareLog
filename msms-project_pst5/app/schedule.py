import os
import csv
import json
import datetime
from PIL import Image
from app.user import User
from app.student import StudentUser
from app.teacher import TeacherUser, Course, Lesson
from app.payment import Payment

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.admin = []
        self.courses = []
        self.attendance = []
        self.finance_log = []
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_course_id = 1
        self.next_lesson_id = 1
        self.next_attendance_id = 1
        self.next_payment_id = 1
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # Student object
                self.students = [StudentUser(s["id"], s["name"], s["username"], s["password"], s["instrument"], s["enrolled_course_ids"]) for s in data.get("students",[])]

                # Teacher object
                self.teachers = [TeacherUser(t["id"], t["name"], t["username"], t["password"],t["speciality"]) for t in data.get("teachers", [])]

                # Staff object
                self.staff = [User(u["username"], u["password"]) for u in data.get("staff", [])]

                # Course object 
                self.courses = [Course(c["id"], c["name"], c["instrument"], c["teacher_id"], c["enrolled_student_ids"], c["lessons"]) for c in data.get("courses", [])]
                
                # Attendance object
                self.attendance = data.get("attendance", [])

                # Finance object
                self.finance_log = [Payment(p["payment_id"], p["student_id"], p["amount"], p["method"], p["receipt"], p["timestamp"])for p in data.get("payment", [])]

                # IDs
                self.next_student_id = data.get("next_student_id", 1)
                self.next_teacher_id = data.get("next_teacher_id", 1)
                self.next_staff_id = data.get("next_staff_id", 1)
                self.next_course_id = data.get("next_course_id", 1)
                self.next_lesson_id = data.get("next_lesson_id", 1)
                self.next_payment_id = data.get("next_payment_id", 1)
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
    
    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        # Create a 'data_to_save' dictionary
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "admin": [adm.__dict__ for adm in self.admin],
            "courses": [c.__dict__ for c in self.courses],
            "attendance":self.attendance,
            "payment": [p.__dict__ for p in self.finance_log],
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
            "next_course_id": self.next_course_id,
            "next_lesson_id": self.next_lesson_id,
            "next_payment_id": self.next_payment_id
        }
        
        # Write the result to the JSON file.
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
            
    def save(self):
        self._save_data()

    def login(self, staff, username, password):
        accounts = {
            "Student": {s.username:s.password for s in self.students},
            "Teacher": {t.username:t.password for t in self.teachers},
            "Staff": {a.username:a.password for a in self.admin}
        }
        acc = accounts[staff]
        if username in acc and acc[username] == password:
            return staff
        else:
            return False

    # --------- Create --------- 
    def add_student(self, name, username, password, instrument, enrolled_courses):
        # Next ID
        student_id = "S" + str(self.next_student_id).zfill(4)

        # Create object
        new_student = StudentUser.create_student_object(student_id, name, username, password, instrument, enrolled_courses)

        # Add object into database
        self.students.append(new_student)
        return True
    
    def add_teacher(self, name, username, password, speciality):
        # Next ID
        teacher_id = "T" + str(self.next_teacher_id).zfill(4)

        # Create object
        new_teacher = TeacherUser.create_teacher_object(teacher_id, name, username, password, speciality)

        # Add object into database
        self.teachers.append(new_teacher)
        return True
    
    def add_course(self, course_id, name, instrument, teacher_id):
        # Next ID
        course_id = "MS" + str(self.next_course_id).zfill(4)

        # Create object
        new_course = Course.create_course_object(course_id, name, instrument, teacher_id)

        # Add object into database
        self.courses.append(new_course)
        return new_course
    
    def add_lesson(self, course_id, lesson_day, lesson_start_time, lesson_room, lesson_remark):
        # Next ID
        lesson_id = "L" + str(self.next_lesson_id).zfill(4)

        # Create object
        new_lesson = Lesson.create_lesson_object(lesson_id, lesson_day, str(lesson_start_time), lesson_room, lesson_remark)

        # Add object into database
        for c in self.courses:
            if c.id == course_id:
                c.lessons.append(new_lesson.to_dict())
                self.next_lesson_id += 1
                return True
        return False

    def add_attendance(self, student_id, course_id, timestamp=None):
        # Get current datetime
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create attendance object
        check_in_record = {
            "student_id": student_id,
            "course_id": course_id,
            "timestamp": timestamp
        }

        # Add into attendance log
        self.attendance.append(check_in_record)
        return True
    
    def add_payment(self, username, amount, method, upload_file):
        """Handles payment record creation and receipt saving."""
        # Ensure finance_log exists
        if self.finance_log is None:
            self.finance_log = []

        # Find student by username
        student = next((s for s in self.students if s.username == username), None)
        if not student:
            return False

        # Generate payment ID
        payment_id = "PID" + str(self.next_payment_id).zfill(4)

        # Create receipts folder
        receipts_dir = "receipts"
        os.makedirs(receipts_dir, exist_ok=True)

        # Save uploaded image
        if upload_file:
            img = Image.open(upload_file)
            file_ext = os.path.splitext(upload_file.name)[1] or ".png"
            save_path = os.path.join(receipts_dir, f"{payment_id}{file_ext}")

            # Avoid overwriting if file already exists
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(receipts_dir, f"{payment_id}_{counter}{file_ext}")
                counter += 1

            img.save(save_path)

            # Create Payment object (store path only)
            new_payment = Payment.create_payment_object(payment_id, student.id, amount, method, save_path)

            if new_payment:
                self.finance_log.append(new_payment)
                self.next_payment_id += 1
                return new_payment
            else:
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
                    s.instrument = update_instrument
                if update_course:
                    s.enrolled_course_ids = sorted(update_course)
                
        # Update enrolled student ids
        for c in self.courses:
            if c.id in update_course and str(update_id) not in c.enrolled_student_ids: 
                c.enrolled_student_ids.append(str(update_id))
            if str(update_id) in c.enrolled_student_ids and c.id not in update_course:
                c.enrolled_student_ids.remove(str(update_id))
                
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

   # --------- Search --------- 
    def search_student(self, s_id):
        student = next((s for s in self.students if str(s.id)== str(s_id)), None)
        
        student_info_dict = {
            "Student ID": student.id,
            "Student Name": student.name,
            "Courses": student.enrolled_course_ids
        }
        
        return student_info_dict
            
    def search_course_by_student_id(self, course_list):
        course_taken = []
        teacher_disp = {t.id:t.name for t in self.teachers}
        
        for c in self.courses:
            if c.id in course_list:
                course = {
                    "Course ID": c.id,
                    "Course Name": c.name,
                    "Teacher": teacher_disp[c.teacher_id]
                }
                course_taken.append(course)
        
        return course_taken

    # -------- Other Feature --------   
    def print_card(self, s_id):
        s_id = str(s_id)
        find_student = next((s for s in self.students if str(s.id) == s_id), None)
        student_info = next((s for s in self.students if str(s.id) == str(s_id)), None)
        course_info = [c for c in self.courses if student_info.id in c.enrolled_student_ids]
        match_teacher = {t.id: t.name for t in self.teachers}

        if find_student:
            filename = f"student{s_id}_card.txt"

            with open(filename, "w") as f:
                f.write("Student Card:\n\n")
                f.write("+" + "="*70 + "+\n")
                f.write("|{:^70}|\n".format("MUSIC SCHOOL ID BADGE"))
                f.write("+" + "="*70 + "+\n")
                f.write("| {:25} {:<42}|\n".format("ID", student_info.id))
                f.write("| {:25} {:<42}|\n".format("Name", student_info.name))
                f.write("+" + "="*70 + "+\n")

                # Add course details dynamically
                for c in course_info:
                    f.write("| {:25} {:<42}|\n".format(f"Course {c.id}", c.name))
                    f.write("|      {:21} {:<42}|\n".format(f"Teacher: ", match_teacher[c.teacher_id]))
                    f.write("|      {:21} {:<42}|\n".format(f"Instrument: ", c.instrument))
                    f.write("|" + " "*70 + "|\n")

                f.write("+" + "="*70 + "+\n")
                f.write("|{:^70}|\n".format("CONGRATULATIONS!"))
                f.write("+" + "="*70 + "+\n")
            return filename
        else:
            return False
        
    def check_in(self, student_id, course_id, timestamp=None):
        # Get current datetime
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create attendance object
        check_in_record = {
            "student_id": student_id,
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

    def get_payment_history(self, student_id):
        """Returns a list of all payments for a given student."""
        student_payments = [p for p in self.finance_log if p.student_id == student_id]
        return student_payments

    @staticmethod
    def payment_to_dict(payment):
        payment_dict = {
            "Payment ID": payment.payment_id,
            "Student ID": payment.student_id,
            "Amount": payment.amount,
            "Method": payment.method,
            "Date of Payment": payment.timestamp
        }
        return payment_dict

    def export_report(self, kind, out_path):
        """Exports a log to a CSV file."""
        print(f"Exporting {kind} report to {out_path}...")
        if kind == "finance":
            data_to_export = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]
        elif kind == "attendance":
            data_to_export = self.attendance
            headers = ["student_id", "course_id", "timestamp"]
        else:
            print("Error: Unknown report type.")
            return
        
        with open(out_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_to_export)

