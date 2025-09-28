# Music School Management System (MSMS) v4

This is a **Streamlit-based web application** for managing a music school.  
It handles different types of users **(students, teachers, staff)**, **supports CRUD operations**, provides **dashboards**, and allows **exporting** and **displaying structured data**.  

---

## How to Run the Program
1. ****If you are a student,...****
- start by registering yourself (username, password)
- update your personal detail (name, instrument, course enrolled)
- view courses available
- check in attendance
- view report card
- give feedback on courses


2. ****If you are a **teacher**,...****
- assume to be staff at this moment
- kindly see 'staff' section


3. ****If you are a **staff**,...****
- use the following to log in
      username: *staff*
      password: *staffPW*
- CRUD operations for students, teachers, courses
- view daily roaster
- print report card
- view the database

4. Continue to explore the rest of the program
---
## Features Overview
- **User Management**
  - Student Page
  - Teacher Page
  - Staff Page
- **Course Management**
  - Create, Read, Update, Delete (CRUD) for courses
- **Dashboard**
  - Overview of students, teachers, and courses
  - Statistics with `st.metric`
- **Display Page**
  - View all data in **DataFrame** and **JSON** format
- **Print Card**
  - Export student details into text files
- **Roaster**
  - Daily timetable generation
  - Attendance check-in for students by subject
- **Future Development**
  - Payment system (planned for next phase)

---

## Code Structure
```python
PST4/
│
├── app/
│ ├── schedule.py
│ ├── user.py
│ └── course.py
│
├── gui/
│ ├── login_pages.py
│ ├── login_gui.py
│ ├── student_gui.py
│ ├── teacher_gui.py
│ ├── staff_gui.py
| └── staff/
|     ├── dashboard.py
|     ├── student_pages.py
|     ├── teacher_pages.py
|     ├── course_pages.py
|     ├── display_pages.py
│     ├── print_card.py
│     ├── roaster_pages.py
│     └── payment_pages.py # (to be continued in phase 5)
│
├── README.md
└── main.py
```

## User Classes

```python
class User:
    # Base Class for All Users
    def __init__(self, username, password, user_id, name):
        # Credentials for Login
        self.username = username
        self.password = password

        # Personal data
        self.id = user_id
        self.name = name


class StaffUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
```

User → Base class for students and teachers

StaffUser → Dedicated class for staff login and management

---

# Student Page

Handles CRUD operations for student users.

## Functions:
```python
register_student() → Register new student

update_student() → Update details of an existing student

delete_student() → Remove a student record

student_launch() → Launch student-specific dashboard and functions
```

---

# Teacher Page

Handles CRUD operations for teacher users.

## Functions:
```python
register_teacher() → Register a new teacher

update_teacher() → Update teacher details (username, password, name, speciality)

delete_teacher() → Remove teacher records

teacher_launch() → Launch teacher-specific dashboard and functions
```

---

# Course Page


Handles CRUD operations for courses.

## Functions:
```python
add_course() → Create new course and assign teacher

update_course() → Modify course details

delete_course() → Remove course

view_courses() → Display list of all available courses
```

---

# Dashboard

The Dashboard Page displays a high-level overview of the system.
It uses st.metric() to display statistics such as:
```python
col1.metric("Total Students", len(manager.students))
col2.metric("Total Teachers", len(manager.teachers))
col3.metric("Total Courses", len(manager.courses))
```

## Purpose:

Quick insights into system usage

Helps staff monitor the music school

--- 

# Display Page

The Display Page shows all data in both tabular and structured formats.

## DataFrame display:
```python
st.dataframe(manager.students)
st.dataframe(manager.teachers)
st.dataframe(manager.courses)
```

## JSON display:
```python
st.json(manager.to_dict())
```

Purpose:

Transparent view of system records

Useful for debugging and auditing

---

# Print Card

Exports a student’s detail card into a text file.

Example Output (text file):
```python
Student ID: 001
Name: Alice Tan
Username: alice123
Courses: Piano, Music Theory
```

## Functions:

export_student_card(student) → Writes details into a .txt file

---

# Roaster

The Roaster Module provides daily scheduling and attendance features.

## Functions:
```python

generate_roaster(day) → Generate timetable for selected day

attendance_check(student_id, subject) → Mark attendance for students
```

## Purpose:

Organize daily lessons

Track student attendance by subject

---
