# Music School Management System (PST1)
## 

```Overview```
This Python program is a simple Music School Front Desk Management System.
It allows staff to register students, enrol them in instruments, add teachers, and search for both students and teachers.
The system uses object-oriented programming (OOP) to create and manage Student and Teacher objects, and stores them in in-memory databases (lists).

🎯 Features
Register New Students – Capture student details and automatically assign a unique ID.

Enrol Existing Students – Add instruments to a student’s enrolment list.

Add Teachers – Register teachers with their speciality instrument.

Lookup Students & Teachers – Search by name, with partial matching support.

Admin View – List all students or teachers (with password protection for students).

Preloaded Test Data – Includes a few teachers and students for quick testing.

🛠 How It Works
Data Models

Student class: Stores student ID, name, and enrolled instruments.

Teacher class: Stores teacher ID, name, and speciality instrument.

In-Memory Database

student_db – List holding all student objects.

teacher_db – List holding all teacher objects.

Core Functions

add_student() – Input validation for new student names and instruments.

add_teacher() – Adds a teacher to the database.

find_students() / find_teachers() – Search functions with exact and partial match handling.

list_students() / list_teachers() – Display all records in a formatted way.

Front Desk Functions

front_desk_register() – Registers and enrols a student.

front_desk_enrol() – Adds an instrument to a student’s record.

front_desk_lookup() – Handles student or teacher lookups based on input.

Main Application Loop

Menu-driven interface for staff to interact with the system.

Password protection for viewing all student data (staff_pw = "staff1234").

Option to quit the program.
