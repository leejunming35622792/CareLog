# pst2_main.py - The Persistent Application
# Lee Jun Ming 35622792
#FIT1056-Sem2-2025

import json
import datetime

# variable
DATA_FILE = "msms.json"
app_data = {}



# --- Data Input ---
def get_studentName():
    while True:
        try:
            student_name = input("Enter Student Name: ")

            if student_name.replace(" ","").isalpha() != True:
                raise ValueError
            break
        except:
            print("Please enter a valid name!\n")
        
    return student_name.lstrip().rstrip().title()

def get_studentID():
    while True:
        try:
            student_id = input("Enter Student ID: ")
            
            if len(student_id) == 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid Student ID!\n")
        
    return student_id

def get_studentCourse():
    student_courses = []

    while True:
        try:
            course_num = input("Number of course enrolled: ")

            if len(course_num) == 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid number!\n")

    for i in range(int(course_num)):
        while True:
            try:
                student_course = input("Enter Course ID: ").upper().strip()
                if len(student_course) == 0:
                    raise ValueError
                student_courses.append(student_course)
                break
            except ValueError:
                print("Please enter a valid Course ID")
    
    return student_courses

def get_courseID():
    while True:
        try:
            course_id = input("Enter Course ID: ")
            break
        except:
            print("Please enter a valid Course ID!\n")

    return course_id

def get_teacherName():
    while True:
        try:
            teacher_name = input("Enter Teacher Name: ")

            if teacher_name.replace(" ","").isalpha() != True:
                raise ValueError
            break
        except:
            print("Please enter a valid name!\n")
        
    return teacher_name.lstrip().rstrip().title()

def get_teacherID():
    while True:
        try:
            teacher_id = input("Enter Teacher ID: ")
            if len(teacher_id) == 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid Teacher ID!\n")

    return teacher_id

def get_teacherSpeciality():
    while True:
        try:
            teacher_speciality = input("Enter Speciality: ")
            if len(teacher_speciality) == 0:
                raise ValueError
            break
        except:
            print("Please enter a valid Speciality!\n")

    return teacher_speciality

def get_teacherYear():
    while True:
        try:
            year_joined = input("Enter Year Joined: ")

            if int(year_joined) > 2025:
                raise ValueError
            
            if len(year_joined) == 0:
                raise ValueError
            
            teacher_year = 2025 - int(year_joined)
            return teacher_year
            
        except ValueError:
            print("Please enter a valid year!\n")
 

      
# --- Full CRUD for Core Data ---
# Teachers
def add_teacher(name, speciality):
    """Adds a teacher dictionary to the data store."""
    # TODO: Get the next teacher ID from app_data['next_teacher_id'].
    teacher_id = app_data['next_teacher_id']

    # TODO: Create a new teacher dictionary with 'id', 'name', and 'speciality' keys.
    new_teacher = {"ID": teacher_id, "Name": name, "Speciality": speciality}

    # TODO: Append the new dictionary to the app_data['teachers'] list.
    app_data['teachers'].append(new_teacher)

    # TODO: Increment the 'next_teacher_id' in app_data.
    app_data['next_teacher_id'] += 1

    print(f"Core: Teacher '{name}' added.")

def update_teacher(teacher_id, **fields):
    """Finds a teacher by ID and updates their data with provided fields."""

    # loop app_data['teachers'] list.
    for teacher in app_data['teachers']:
        # if teacher's 'id' matches teacher_id:
        if teacher['ID'] == teacher_id:

            # Use the .update() method on the teacher dictionary to apply the 'fields'.
            teacher.update(fields)
            print(f"Teacher {teacher_id} updated.")
            return
        
    print(f"Error: Teacher with ID {teacher_id} not found.")

def remove_teacher(teacher_id):
    """Removes a teacher from the data store."""
    app_data['teachers'] = [teacher for teacher in app_data['teachers'] if teacher['ID'] != teacher_id]

#Students
def update_student(student_id, student_course):
    # loop app_data['student'] list
    for student in app_data['students']:
        if student['ID'] == student_id:
            student["Course"] = student_course
            print(f"Student with ID '{student_id}' updated")
            return 
    print("Error: Student with ID {student_id} not found.")

def remove_student(student_id):
    """Removes a student from the data store."""
    all_id = [student["ID"] for student in app_data["students"]]

    if int(student_id) not in all_id:
        print("Failed!")
        print(f"Alert - ID '{student_id}' has not been registered.")

    else:
        app_data["students"] = [student for student in app_data["students"] if student["ID"] != student_id]
        print("Deleted successfully!\n")



# --- Core Persistence Engine ---
def load_data(path=DATA_FILE):
    global app_data

    try:
        with open(path, "r") as f:
            app_data = json.load(f)
            print("Data loaded successfully.")

    except FileNotFoundError:
        print("Data file not found. Initializing with default structure.")

        app_data = {
            "students": [],
            "teachers": [],
            "attendance": [],
            "next_student_id": 1,
            "next_teacher_id": 1
        }

def save_data(path=DATA_FILE):
    with open(path, "w") as f:
        json.dump(app_data, f, indent=4)
    print("Data saved successfully.")
