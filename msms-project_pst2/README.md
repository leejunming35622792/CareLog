# FIT1056 Semester 2 2025 — Student & Teacher Management System

This is a Python-based console application for managing **students**, **teachers**, and their **courses**.  
The program provides a simple text-based interface to add, update, search, and display records.  
It is designed to demonstrate basic data structures, input validation, and program flow control in Python.

---

## Overview

The program is intended for educational use as part of the FIT1056 coursework.  
It uses Python's built-in data structures (lists and dictionaries) to store records in memory without an external database.  
When running, all information is kept in a global `app_data` dictionary that contains separate lists for students and teachers.

The key focus of this project:
- Practicing function-based program design
- Applying input validation
- Handling user input safely
- Maintaining readable and modular code
- Using Git for version control

---

## Features

### Student Management
- **Add a student** — Create a new record with name, ID, and a list of enrolled course codes.
- **Update a student** — Modify existing student details, such as changing their enrolled courses.
- **Search by ID** — Find a student record by entering their student ID.
- **Display all students** — Print a list of all student records currently stored.
- **Delete a student** — Remove a student record from the system.

### Teacher Management
- **Add a teacher** — Create a new record with name, ID, teaching speciality, and the year they joined.
- **Update a teacher** — Modify an existing teacher’s details.
- **Search by ID** — Find a teacher record by entering their teacher ID.
- **Display all teachers** — Print a list of all teacher records currently stored.
- **Delete a teacher** — Remove a teacher record from the system.

### Course Handling
- Store courses for students as a list of course codes (e.g., `1056`, `1058`).
- Check if a course exists in a student’s record.
- Format course lists for display (comma-separated).

---

## Requirements

- Python 3.8 or later
- Uses only built-in Python modules such as `datetime`
- No internet connection required for operation

---

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/leejunming35622792/FIT1056-Sem2-2025.git
   cd FIT1056-Sem2-2025
