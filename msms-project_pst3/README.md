# Music School Management System (MSMS v3 - OOP Edition)

## 1. Overview
The **Music School Management System (MSMS)** is a Python command-line program that uses **Object-Oriented Programming (OOP)** to help music schools manage:

- Students
- Teachers
- Courses
- Lessons
- Attendance logs

The program reads and writes data from a JSON file so that all information is persistent between runs.  
It is designed to be simple and usable by front desk staff or administrators.

---

## 2. Features

### 2.1 Register New Student or Teacher
- **Add Student**
  - Input student name (only letters allowed).
  - Assign student to one or more existing courses.
- **Add Teacher**
  - Input teacher name.
  - Assign teacher a speciality (e.g., Piano, Violin).

Validation rules:
- Names must contain letters only.
- Courses and teachers must already exist before students can be registered.

---

### 2.2 Update Student or Teacher
- **Update Student**
  - Change student’s enrolled course(s).
  - Confirmation required before changes are saved.
- **Update Teacher**
  - Modify a teacher’s speciality.

---

### 2.3 Delete Student or Teacher
- Remove a student or teacher permanently from the system.
- Confirmation is required to avoid accidental deletions.

---

### 2.4 Student Check-In (Attendance)
- Record when a student attends a class.
- Requires both:
  - Student ID
  - Course ID (must match the student’s enrolled courses)
- Automatically records a timestamp (date and time).

---

### 2.5 View Daily Roster
- Displays all lessons scheduled for a specific day (e.g., Monday).
- Includes:
  - Day of the lesson
  - Course ID
  - Lesson venue

---

### 2.6 View All Records
Display complete records of:
1. Students (ID, Name, Enrolled Courses)
2. Teachers (ID, Name, Speciality)
3. Courses (ID, Name, Instrument, Teacher ID, Enrolled Students)
4. Attendance logs (Student ID, Course ID, Timestamp)

---

### 2.7 Add New Course
- Provide:
  - Unique Course ID
  - Course name
  - Instrument (letters only)
  - Teacher ID (must already exist)
- Course is then linked to the assigned teacher.

---

### 2.8 Update Lesson Info
- Add or update lessons for each course:
  - Day (e.g., Monday)
  - Venue
  - Additional notes

These lessons are displayed in the daily roster.

---

### 2.9 Quit
- Exit the system safely.
- Confirms before closing to prevent losing unsaved changes.

---

## 3. Program Flow

1. **Program start**  
   Displays a guide: add teachers → courses → students.

2. **Main Menu Options**

```    
===== MSMS v3 (Object-Oriented) =====
1 - Register New Student/Teacher
2 - Update Student/Teacher
3 - Delete Student/Teacher
4 - Check-in Student
5 - View Daily Roster
6 - View All
7 - Add New Course
8 - Update Lesson Info
q - Quit (Exit Key)
```


3. **Data Storage**  
   - All information is saved into a JSON file (`data.json`).
   - File is automatically created if missing.
   - Data is reloaded every time the program runs.

---

## 4. Input Rules and Validation

- **Names and instruments**: must contain letters only (no numbers or special characters).
- **IDs**:
  - Students and teachers have numeric IDs.
  - Course IDs can be alphanumeric (commonly uppercase letters and numbers).
- **Quit**: Enter `q` at any prompt to cancel the operation.
- **Confirmation**: All critical actions (update, delete, course changes) require a yes/no confirmation.

---

## 5. Example Usage

### 5.1 Adding a Teacher
```
--- Add New Teacher ---
Enter Teacher Name: John Smith
Enter Speciality: Piano
Changes made successfully.
```

### 5.2 Adding a Course
```
--- Add New Course ---
Enter Course ID: P101
Enter Course Name: Classical Piano
Enter Instrument: Piano
Enter Teacher ID: 1
Changes made successfully.
```

### 5.3 Adding a Student
```
--- Add New Student ---
Enter Student Name: Alice
Number of course enrolled: 1
Enter Course ID: P101
Changes made successfully.
```

### 5.4 Student Check-in
```
--- Check In Student ---
Enter Student ID: 1
Courses under Student ID 1: ['P101']
Enter Course ID: P101
Successfully Checked In!
Student ID: 1
Course ID: P101
Date/Time: 2025-08-26 18:22:30
```

---

## 6. Requirements
- Python 3.10 or later (match-case statements are used).
- JSON file for data storage.
- Runs in any terminal or command prompt.

---

## 7. Project Structure
project/
│── main.py # Main program (menu and user interaction)
│── app/
│ ├── student.py # StudentUser class
│ ├── teacher.py # TeacherUser class
│ ├── course.py # Course class
│ ├── lesson.py # Lesson class
│ ├── schedule.py # ScheduleManager (loads/saves data)
│── data.json # Data storage file (auto-generated if missing)

---

## 8. Notes for Users

- Always add teachers first, then courses, then students.
- A course cannot be created without a valid teacher.
- A student cannot be created without a valid course.
- Attendance requires the student to be enrolled in that course.
- Daily roster only works if lessons are properly assigned to courses.

---


