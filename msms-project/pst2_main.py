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
