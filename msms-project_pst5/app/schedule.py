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
    """Main controller for data management and business logic."""

    def __init__(self, data_path="data/msms.json"):
        # File location for persistent data
        self.data_path = data_path

        # In-memory storage
        self.students = []
        self.teachers = []
        self.admin = []
        self.courses = []
        self.attendance = []
        self.finance_log = []

        # Auto-increment ID counters
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_course_id = 1
        self.next_lesson_id = 1
        self.next_attendance_id = 1
        self.next_payment_id = 1

        self._load_data()

    # ---------- Data Persistence ----------

    def _load_data(self):
        """Load all data from JSON file into memory objects."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)

                # Students
                self.students = [
                    StudentUser(s["id"], s["name"], s["username"], s["password"],
                                s["instrument"], s["enrolled_course_ids"])
                    for s in data.get("students", [])
                ]

                # Teachers
                self.teachers = [
                    TeacherUser(t["id"], t["name"], t["username"], t["password"],
                                t["speciality"])
                    for t in data.get("teachers", [])
                ]

                # Staff
                self.staff = [User(u["username"], u["password"])
                              for u in data.get("staff", [])]

                # Courses
                self.courses = [
                    Course(c["id"], c["name"], c["instrument"], c["teacher_id"],
                           c["enrolled_student_ids"], c["lessons"])
                    for c in data.get("courses", [])
                ]

                # Attendance & Payments
                self.attendance = data.get("attendance", [])
                self.finance_log = [
                    Payment(p["payment_id"], p["student_id"], p["amount"],
                            p["method"], p["receipt"], p["timestamp"])
                    for p in data.get("payment", [])
                ]

                # Auto ID tracking
                self.next_student_id = data.get("next_student_id", 1)
                self.next_teacher_id = data.get("next_teacher_id", 1)
                self.next_staff_id = data.get("next_staff_id", 1)
                self.next_course_id = data.get("next_course_id", 1)
                self.next_lesson_id = data.get("next_lesson_id", 1)
                self.next_payment_id = data.get("next_payment_id", 1)

        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")

    def _save_data(self):
        """Convert in-memory objects into dicts and save back to JSON."""
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "admin": [adm.__dict__ for adm in self.admin],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance,
            "payment": [p.__dict__ for p in self.finance_log],
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
            "next_course_id": self.next_course_id,
            "next_lesson_id": self.next_lesson_id,
            "next_payment_id": self.next_payment_id
        }

        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)

    def save(self):
        """Public method to trigger data save."""
        self._save_data()

    # ---------- Authentication ----------

    def login(self, staff, username, password):
        """Validate credentials for students, teachers, or staff."""
        accounts = {
            "Student": {s.username: s.password for s in self.students},
            "Teacher": {t.username: t.password for t in self.teachers},
            "Staff": {a.username: a.password for a in self.admin}
        }

        acc = accounts[staff]
        if username in acc and acc[username] == password:
            return staff
        return False

    # ---------- Create Operations ----------

    def add_student(self, name, username, password, instrument, enrolled_courses):
        """Create and register a new student."""
        student_id = "S" + str(self.next_student_id).zfill(4)
        new_student = StudentUser.create_student_object(
            student_id, name, username, password, instrument, enrolled_courses
        )
        self.students.append(new_student)
        return True

    def add_teacher(self, name, username, password, speciality):
        """Create and register a new teacher."""
        teacher_id = "T" + str(self.next_teacher_id).zfill(4)
        new_teacher = TeacherUser.create_teacher_object(
            teacher_id, name, username, password, speciality
        )
        self.teachers.append(new_teacher)
        return True

    def add_course(self, course_id, name, instrument, teacher_id):
        """Create and register a new course."""
        course_id = "MS" + str(self.next_course_id).zfill(4)
        new_course = Course.create_course_object(course_id, name, instrument, teacher_id)
        self.courses.append(new_course)
        return new_course

    def add_lesson(self, course_id, lesson_day, lesson_start_time, lesson_room, lesson_remark):
        """Attach a lesson to an existing course."""
        lesson_id = "L" + str(self.next_lesson_id).zfill(4)
        new_lesson = Lesson.create_lesson_object(
            lesson_id, lesson_day, str(lesson_start_time), lesson_room, lesson_remark
        )

        for c in self.courses:
            if c.id == course_id:
                c.lessons.append(new_lesson.to_dict())
                self.next_lesson_id += 1
                return True
        return False

    def add_attendance(self, student_id, course_id, timestamp=None):
        """Record attendance for a student in a course."""
        timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {"student_id": student_id, "course_id": course_id, "timestamp": timestamp}
        self.attendance.append(record)
        return True

    def add_payment(self, username, amount, method, upload_file):
        """Create payment entry and save uploaded receipt image."""
        if self.finance_log is None:
            self.finance_log = []

        student = next((s for s in self.students if s.username == username), None)
        if not student:
            return False

        payment_id = "PID" + str(self.next_payment_id).zfill(4)

        # Ensure folder exists
        receipts_dir = "receipts"
        os.makedirs(receipts_dir, exist_ok=True)

        # Save image safely
        if upload_file:
            img = Image.open(upload_file)
            file_ext = os.path.splitext(upload_file.name)[1] or ".png"
            save_path = os.path.join(receipts_dir, f"{payment_id}{file_ext}")

            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(receipts_dir, f"{payment_id}_{counter}{file_ext}")
                counter += 1

            img.save(save_path)

            new_payment = Payment.create_payment_object(
                payment_id, student.id, amount, method, save_path
            )

            if new_payment:
                self.finance_log.append(new_payment)
                self.next_payment_id += 1
                return new_payment
        return False

    # ---------- Update Operations ----------

    def update_student(self, username, password, update_id, update_name, update_instrument, update_course):
        """Modify student profile and update related course enrollments."""
        update_course = update_course or []
        for s in self.students:
            if str(s.id) == str(update_id) or s.username == username:
                if username: s.username = username
                if password: s.password = password
                if update_name: s.name = update_name
                if update_instrument: s.instrument = update_instrument
                s.enrolled_course_ids = sorted(update_course)

        # Synchronize student list in each course
        for c in self.courses:
            if c.id in update_course and str(update_id) not in c.enrolled_student_ids:
                c.enrolled_student_ids.append(str(update_id))
            if str(update_id) in c.enrolled_student_ids and c.id not in update_course:
                c.enrolled_student_ids.remove(str(update_id))
        return True

    def update_teacher(self, username, password, update_id, update_name, update_speciality):
        """Modify teacher account information."""
        for t in self.teachers:
            if str(t.id) == str(update_id) or t.username == username:
                if username: t.username = username
                if password: t.password = password
                if update_name: t.name = update_name
                if update_speciality: t.speciality = update_speciality
                return True
        return False

    def update_course(self, update_course_id, update_name, update_instrument, update_teacher):
        """Modify existing course details."""
        for c in self.courses:
            if str(c.id) == str(update_course_id):
                if update_name: c.name = update_name
                if update_instrument: c.instrument = update_instrument
                if update_teacher: c.teacher_id = update_teacher
                return True
        return False

    def update_lesson(self, update_lessonID, update_day, update_starttime, update_room, update_remark):
        """Update lesson timing or description."""
        for c in self.courses:
            for l in c.lessons:
                if str(l["lesson-id"]) == str(update_lessonID):
                    if update_day: l["day"] = update_day
                    if update_starttime: l["start_time"] = str(update_starttime)
                    if update_room: l["room"] = update_room
                    if update_remark: l["remark"] = update_remark
                    return True
        return False

    # ---------- Delete Operations ----------
    def remove_student(self, s_id):
        """Delete student record."""
        student = next((s for s in self.students if str(s.id) == str(s_id)), None)
        if student:
            self.students.remove(student)
            return True
        return False

    def remove_teacher(self, t_id):
        """Delete teacher record."""
        self.teachers = [t for t in self.teachers if str(t.id) != str(t_id)]
        return True

    def delete_course(self, delete_course_id):
        """Delete course from list."""
        self.courses = [c for c in self.courses if str(c.id) != str(delete_course_id)]
        return True

    def delete_lesson(self, delete_lessonID):
        """Delete a lesson from its course."""
        for c in self.courses:
            c.lessons = [l for l in c.lessons if l["lesson-id"] != delete_lessonID]
            return True

    # ---------- Search & Query ----------

    def search_student(self, s_id):
        """Find student by ID and return summary."""
        student = next((s for s in self.students if str(s.id) == str(s_id)), None)
        return {
            "Student ID": student.id,
            "Student Name": student.name,
            "Courses": student.enrolled_course_ids
        }

    def search_course_by_student_id(self, course_list):
        """List courses taken by a given student."""
        teacher_disp = {t.id: t.name for t in self.teachers}
        return [
            {"Course ID": c.id, "Course Name": c.name, "Teacher": teacher_disp[c.teacher_id]}
            for c in self.courses if c.id in course_list
        ]

    def get_all_lessons(self, course_id):
        """Retrieve all lessons for a given course."""
        lessons = []
        course = next((c for c in self.courses if c.id == course_id), None)
        if not course:
            return lessons

        for l in (course.lessons or []):
            lesson_id = l.get("lesson-id") or l.get("lesson_id")
            lessons.append({
                "Lesson ID": lesson_id or "",
                "Day": l.get("day", ""),
                "Time": l.get("start_time", "") or l.get("time", ""),
                "Room": l.get("room", ""),
                "Remark": l.get("remark", "")
            })
        return lessons

    # ---------- Other Features ----------

    def print_card(self, s_id):
        """Generate a text-based student ID card."""
        s_id = str(s_id)
        student_info = next((s for s in self.students if str(s.id) == s_id), None)
        if not student_info:
            return False

        course_info = [c for c in self.courses if student_info.id in c.enrolled_student_ids]
        match_teacher = {t.id: t.name for t in self.teachers}

        filename = f"student{s_id}_card.txt"
        with open(filename, "w") as f:
            f.write("Student Card:\n\n")
            f.write("+" + "=" * 70 + "+\n")
            f.write("|{:^70}|\n".format("MUSIC SCHOOL ID BADGE"))
            f.write("+" + "=" * 70 + "+\n")
            f.write("| {:25} {:<42}|\n".format("ID", student_info.id))
            f.write("| {:25} {:<42}|\n".format("Name", student_info.name))
            f.write("+" + "=" * 70 + "+\n")

            for c in course_info:
                f.write("| {:25} {:<42}|\n".format(f"Course {c.id}", c.name))
                f.write("|      {:21} {:<42}|\n".format("Teacher:", match_teacher[c.teacher_id]))
                f.write("|      {:21} {:<42}|\n".format("Instrument:", c.instrument))
                f.write("|" + " " * 70 + "|\n")

            f.write("+" + "=" * 70 + "+\n")
            f.write("|{:^70}|\n".format("CONGRATULATIONS!"))
            f.write("+" + "=" * 70 + "+\n")
        return filename

    def check_in(self, student_id, course_id, timestamp=None):
        """Record a check-in entry (same as attendance)."""
        timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {"student_id": student_id, "course_id": course_id, "timestamp": timestamp}
        self.attendance.append(record)
        return True

    def search_function(self, staff, search_keyword):
        """Generic name-based search for students or teachers."""
        if staff == "S":
            return [
                {"Student ID": s.id, "Student Name": s.name, "Courses Enrolled": s.enrolled_course_ids}
                for s in self.students if search_keyword.lower() in s.name.lower()
            ]
        if staff == "T":
            return [
                {"Teacher ID": t.id, "Teacher Name": t.name, "Speciality": t.speciality}
                for t in self.teachers if search_keyword.lower() in t.name.lower()
            ]

    def get_payment_history(self, student_id):
        """Return all payment records for a student."""
        return [p for p in self.finance_log if p.student_id == student_id]

    @staticmethod
    def payment_to_dict(payment):
        """Convert Payment object to dictionary."""
        return {
            "Payment ID": payment.payment_id,
            "Student ID": payment.student_id,
            "Amount": payment.amount,
            "Method": payment.method,
            "Date of Payment": payment.timestamp
        }

    def export_report(self, kind, out_path):
        """Export attendance or finance logs to CSV file."""
        print(f"Exporting {kind} report to {out_path}...")
        if kind == "finance":
            data = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]
        elif kind == "attendance":
            data = self.attendance
            headers = ["student_id", "course_id", "timestamp"]
        else:
            print("Unknown report type.")
            return

        with open(out_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    def save_feedback(self, feedback):
        """Placeholder for feedback submission logic."""
        base_dir = "data/feedback"
        os.makedirs(base_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        message = f"{timestamp} - {feedback}"

        file_dir = os.path.join(base_dir, "feedback.txt")

        with open(file_dir, 'a', encoding='utf-8') as f:
            f.write(message)

    def load_feedback(self):
        """Load and parse all feedback entries from file."""

        base_dir = os.path.dirname(self.data_path)
        file_path = os.path.join(base_dir, "feedback.txt")

        if not os.path.exists(file_path):
            return []

        feedback_list = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Expected format: timestamp - course_id - course_name - message
                parts = line.split(" - ", 3)
                if len(parts) == 4:
                    timestamp, course_id, course_name, message = parts
                    feedback_list.append({
                        "timestamp": line[0:19],
                        "course_id": line[22:27],
                        "course_name": course_name,
                        "message": message
                    })
                else:
                    feedback_list.append({"timestamp": "Unknown", "course_id": "N/A", "course_name": "N/A", "message": line})

        return feedback_list


