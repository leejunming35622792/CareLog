# Music School Management System (MSMS.v5)

**MSMS.v5** is a **Streamlit-based web application** designed for managing a music school.  
It supports **multi-user roles (Student, Teacher, Staff)**, provides **CRUD operations**, **data dashboards**, and **report generation**.

---
## MSMSv5 vs MSMSv4
**Login:** The latest version require all new users to input their details before getting started.

**Payment:** A new page is launched where students can upload their payment records and view their past payment records (_image supported_)

**Roaster:** A formatted schedule timetable is added to Roaster Page, where students and teachers can have a better overview instead of looking on the _dataframe_

**Feedback**: A new page is launched where students can feedback about the courses.

---
## 🧠 Development Environment

| Component | Version / Notes |
|------------|----------------|
| **Python** | 3.10+ recommended *(3.8+ minimum for Streamlit support)* |
| **Streamlit** | 1.36.0+ *(for GUI and web-based interactivity)* |
| **Pandas** | 2.x *(for structured data tables, CRUD operations)* |
| **Pillow (PIL)** | 10.x *(for image display and management in GUI)* |
| **Datetime** | Built-in *(for timestamps, attendance, schedules)* |
| **OS / CSV / JSON** | Built-in *(for data storage, export, and file ops)* |

---

## 📦 Key Python Libraries Used

### 1. `os`
**Purpose:**  
Handles file paths and directories for saving data and images.  

**Example:**
```python
import os
os.path.exists("data/students.csv")
```

### 2. `csv`
**Purpose:**
Reads and writes .csv files for storing structured data (students, teachers, etc).

**Example:**

```python
import csv
csv.writer(file).writerow(["id", "name", "course"])
```

### 3. ```json```
**Purpose:**
Used for saving data in JSON format — easy for backup and loading structured data.

Example:

```python
import json
json.dump(data, open("students.json", "w"))
```

### 4. ```datetime```
**Purpose:**
Manages timestamps, attendance, and scheduling features.

Example:

```
import datetime
datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

### 5. ```PIL (Pillow)```
Purpose:
Handles and displays images in the Streamlit app.

Example:

```
from PIL import Image
st.image(Image.open("img/logo.png"))
```

### 6. ```pandas```
**Purpose:**
Manages and displays tabular data (students, teachers, courses).

Example:

```
import pandas as pd
df = pd.DataFrame(manager.students)
st.dataframe(df)
```

### 7. ```streamlit```
**Purpose:**
Main UI framework for building the web app (forms, buttons, dashboards).

Example:

```
import streamlit as st
st.form("login")
st.text_input("Username:")
```

🧩 ### Project Modules Imported
```
from app.user import User
from app.student import StudentUser
from app.teacher import TeacherUser, Course, Lesson
from app.payment import Payment
```

| Module | Purpose |
|------------|----------------|
|User|	Base class for all users (common attributes like username, password)|
|StudentUser|	Handles student-specific details and functions (attendance, course enrolment)|
|TeacherUser|	Handles teacher-related features (schedule, courses taught)
|Course, Lesson|	Represent music courses and individual lessons
|Payment|	Handles student payment and fee tracking (future phase)

---
---
# How to Run the Program
## If you are a student:
Start by registering yourself (username, password)

Update your personal details (name, instrument, enrolled courses)

View available courses, and lessons

Check in attendance

View your report card

Give feedback on courses

## If you are a teacher:
**Currently treated as staff (teaching management access)**

View assigned courses and lessons

## If you are staff:
Use the following credentials:

````
python
username: staff  
password: staffPW
````
Manage (CRUD) operations for students, teachers, and courses

View daily roaster (schedule)

Print report cards

Access the full database view

---

## Features Overview - User Management
Student Page

Teacher Page

Staff Page

**Course Management**
Create, Read, Update, Delete (CRUD) courses
---
📊 **Dashboard**
Displays key metrics (students, teachers, courses)

Uses st.metric for statistics visualization
---
🗂️ **Display Page**
View all data in both DataFrame and JSON formats
---
🖨️ **Print Card**
Export student details into .txt files
---
🗓️ **Roaster**
View formatted schedule timetable, and generate daily timetables

Allow attendance check-in by course
---
💡 **Future Development**
Payment & Billing System (planned for next phase)
```
🧱 Code Structure
bash
Copy code
PST4/
│
├── app/
│   ├── schedule.py
│   ├── user.py
│   └── course.py
│
├── gui/
│   ├── login_pages.py
│   ├── login_gui.py
│   ├── student_gui.py
│   ├── teacher_gui.py
│   ├── staff_gui.py
│   └── staff/
│       ├── dashboard.py
│       ├── student_pages.py
│       ├── teacher_pages.py
│       ├── course_pages.py
│       ├── display_pages.py
│       ├── print_card.py
│       ├── roaster_pages.py
│       └── payment_pages.py  # (to be added in phase 5)
│
├── README.md
└── main.py
```

👥 #python
```
class User:
    # Base Class for All Users
    def __init__(self, username, password, user_id, name):
        self.username = username
        self.password = password
        self.id = user_id
        self.name = name
```
```
class StaffUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
```
User → Base class for both students and teachers

StaffUser → Handles staff login and management

## Student Page
Handles student registration, updates, and dashboard.

Functions:
```
register_student()  # Register a new student
update_student()    # Update student details
delete_student()    # Remove student record
student_launch()    # Launch student dashboard
```

## Teacher Page
Manages teacher profiles and courses taught.

Functions:
```
register_teacher()  # Add new teacher
update_teacher()    # Update teacher info
delete_teacher()    # Remove teacher
teacher_launch()    # Launch teacher dashboard
```

## Course Page
Handles course creation and updates.

Functions:
```
add_course()     # Create a new course
update_course()  # Modify details
delete_course()  # Delete existing course
view_courses()   # View all available courses
```

## Dashboard
Displays high-level statistics using Streamlit metrics.

```
col1.metric("Total Students", len(manager.students))
col2.metric("Total Teachers", len(manager.teachers))
col3.metric("Total Courses", len(manager.courses))
```
**Purpose:**

Quick insights into school performance

Useful for admin overview

## Display Page
Shows full database content in visual and structured forms.

Example:
```
st.dataframe(manager.students)
st.dataframe(manager.teachers)
st.dataframe(manager.courses)
st.json(manager.to_dict())
```

**Purpose:**
Transparency

Debugging and data validation

## Print Card
Exports student details into .txt files.

Example Output:
```
Student ID: 001
Name: Alice Tan
Username: alice123
Courses: Piano, Music Theory
```
Function:
```
export_student_card(student)
```

## Roaster
Handles scheduling and attendance marking.

Functions:
```
generate_roaster(day)           # Generate daily timetable
attendance_check(student_id)    # Mark attendance
```

**Purpose:**

## Organize lessons

Track student attendance

## Payment System

Track student fees and due dates

Generate payment receipts

Display payment summaries in dashboard