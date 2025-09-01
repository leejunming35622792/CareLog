# main.py - The View Layer
from app.student import StudentUser
from app.teacher import TeacherUser
from app.schedule import ScheduleManager
import datetime

# Declaration
manager = ScheduleManager()
all_students = [f"Student ID: {s.id}, Student Name: {s.name},Enrolled Courses: {s.enrolled_course_ids}" for s in manager.students]
all_students_id = [s.id for s in manager.students]
all_teacher_name = [[t.id, t.name, t.speciality] for t in manager.teachers]
all_courses = [c for c in manager.courses]
all_attendance = [a for a in manager.attendance_log]

# Additional Feature
def check_course():
    all_courses = [c for c in manager.courses]
    if all_courses == []:
        print("Please add a new course first.")
        return False
    return True

def confirm_action():
    while True:
        print("1 - Proceed with Changes\n2 - Exit")
        action = input("Choice: ")
        if action == "1":
            print("Changes made successfully.")
            return True
        elif action == "2":
            print("Changes not made.")
            return main()
        else:
            print("Please enter 1 or 2 only.\n")

# Feature 1 - Register
def get_student_name():
        while True:
            student_name = input("Enter Student Name: ")
            try:
                if student_name.replace(" ","").isalpha() != True:
                    raise ValueError
                if student_name in [s.name for s in manager.students]:
                    print(f"{student_name} has been registered before.")
                    raise ValueError 
                break
            except ValueError:
                print("Please enter a valid name!\n")
        return student_name.lstrip().rstrip().title()

def get_enrolled_course():
        student_courses = []
        # To get number of courses
        while True:
            course_num = input("Number of course enrolled: ")
            try:
                course_num = int(course_num)  
                if course_num <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid number!\n")
        # To get input of courses
        for i in range(int(course_num)):
            while True:
                student_course = input("Enter Course ID: ")
                try:
                    if student_course == "q":
                        print("Changes not made.")
                        return main()
                    if student_course.upper() not in [c.id for c in manager.courses]:
                        print(f"Course '{student_course}' not found.")
                        raise ValueError
                    if len(student_course) == 0:
                        print("Please enter a valid number.")
                        raise ValueError
                    student_courses.append(student_course.strip().upper())
                    break
                except ValueError:
                    print("Please try again\n")
        return student_courses

def add_student():
    print("\n--- Add New Student ---")
    name = get_student_name()
    course = get_enrolled_course()
    return name, course

def get_teacher_name():
        while True:
            teacher_name = input("Enter Teacher Name: ")
            try:
                if teacher_name.replace(" ","").isalpha() != True:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid name!\n")
        return teacher_name.lstrip().rstrip().title()

def get_teacher_speciality():
    while True:
        teacher_speciality = input("Enter Speciality: ")
        try:
            if teacher_speciality.replace(" ","").isalpha() != True:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid speciality!\n")
    return teacher_speciality.lstrip().rstrip().title()

def add_teacher():
    print("\n--- Add New Teacher ---")
    name = get_teacher_name()
    speciality = get_teacher_speciality()
    return name, speciality

# Feature 2 - Update
def get_student_id():
    while True:
        student_id = input("Enter Student ID: ")
        try:
            if student_id == "q":
                print("Changes not made.")
                return main()
            if student_id.isdigit() == False:
                raise TypeError
            if int(student_id) not in [s.id for s in manager.students]:
                raise ValueError
            break
        except ValueError:
            print(f"Student ID '{student_id}' not found.\n")
        except TypeError:
            print("Please enter a valid number\n")
    return student_id

def get_teacher_id():
    while True:
        teacher_id = input("Enter Teacher ID: ")
        try:
            if teacher_id == "q":
                print("Changes not made.")
                return main()
            if teacher_id.isdigit() == False:
                raise TypeError
            if int(teacher_id) > manager.next_teacher_id - 1:
                raise ValueError
            break
        except ValueError:
            print(f"Teacher ID '{teacher_id}' not found.\n")
        except TypeError:
            print("Please enter a valid number\n")
    return teacher_id

def switch_course(manager, student_id, from_course_id, to_course_id):
    # access the enrolled courses
    # as only one element, print index 0
    find_name_course = [s.enrolled_course_ids for s in manager.students if s.id == int(student_id)][0]

    # without .copy(), original_course is a reference
    # with .copy(), original course is a same list and stored in memory
    original_course = find_name_course.copy()

    # replace "109" with "190"
    if from_course_id in find_name_course:
        find_name_course.remove(from_course_id)
        find_name_course.append(to_course_id)
        find_name_course.sort()
        print(f"\nFrom {original_course} -> To {find_name_course}")
        action = confirm_action()
        return action
    else:
        print(f"Failed, as Course '{from_course_id}' is not found.")
        print("Please try again.")
        return main()

def update_teacher(teacher_id, to_speciality):
    for t in manager.teachers:
        if t.id == int(teacher_id):
            t.speciality = to_speciality
            action = confirm_action()
            return action

# Feature 3 - Delete
def delete_student(student_id):
    # To load all students
    all_students = [s for s in manager.students if s.id != int(student_id)]
    manager.students = all_students
    action = confirm_action()
    return action

def delete_teacher(teacher_id):
    all_teachers = [t for t in manager.teachers if t.id != int(teacher_id)]
    manager.teachers = all_teachers
    action = confirm_action()
    return action

# Feature 4 - Check-in 
def check_in(student_id, course_id, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_in_record = {
        "Student ID": int(student_id),
        "Course ID": course_id,
        "Timestamp": timestamp
    }
    manager.attendance_log.append(check_in_record)

# Feature 6 - View All
def get_course_id(remark):
    while True:
        if remark == "new":
            course_id = input(f"Enter Course ID: ").upper()
            try:
                if course_id == "Q":
                    print("----------\nChanges not made.\n----------")
                    return main()
                if course_id.upper() in [c.id for c in manager.courses]:
                    print(f"Course '{course_id}' has been added.")
                return course_id.upper()
            except:
                print("Please try again.\n")
        elif remark == "view":
            all_courses_id = [c.id for c in manager.courses]
            print(f"Courses Available: {all_courses_id}")
            course_id = input(f"Enter Course ID: ").upper()
            try:
                if course_id == "Q":
                    print("----------\nChanges not made.\n----------")
                    return main()
                if course_id not in [c.id for c in manager.courses]:
                    print(f"Course ID '{course_id}' not found.")
                    raise ValueError
                return course_id.upper()
            except:
                print("Please try again.\n")
        else:
            all_courses_id = [c.id for c in manager.courses]
            if remark != "":
                print(f"Courses Available: {all_courses_id}" + "\n")
            course_id = input(f"Enter Course ID{remark}: ").upper()
            try:
                if course_id == "Q":
                    print("----------\nChanges not made.\n----------")
                    return main()
                if course_id not in [c.id for c in manager.courses]:
                    print(f"Course ID '{course_id}' not found.")
                    raise ValueError
                return course_id.upper()
            except:
                print("Please try again.\n")
    
def view_all_data(choice):
    match (choice):
        case "1":
            all_students = [f"Student ID: {s.id}, Student Name: {s.name},Enrolled Courses: {s.enrolled_course_ids}" for s in manager.students]
        case "2":
            all_teacher_name = [t.name for t in manager.teachers]
            print(f"Teacher Names: {all_teacher_name}")
        case "3":
            all_courses = [c for c in manager.courses]
            print(all_courses)
        case "4":
            all_attendance = [a for a in manager.attendance_log]
            print(all_attendance)
        case "5":
            pass

# Feature 5 - View Daily Roaster
def get_day(prompt):
    while True:
        day = input(prompt).title()
        if day == "Q":
            return main()
        if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            print("Invalid Input!")
        else:
            return day.title()

def front_desk_daily_roster(manager, day):  
    #Displays a pretty table of all lessons on a given day.
    print(f"\n--- Daily Roster for {day} ---")
    # To find the courses that its lesson is on that day
    day_courses = [[c.id,c.lessons] for c in manager.courses]
    print("Day".ljust(10), "|  Course".ljust(15), "|  Venue".ljust(10))
    for day_course in day_courses:
        current_course = day_course[0]
        for lesson_info in day_course[1]:
            if lesson_info.get("Day") == day:
                print(day.ljust(10), f"|  {current_course}".ljust(15),f"|  {lesson_info.get("Venue")}".ljust(10))

    # Notice: This code does not need to change. It doesn't care where the Course class lives.
    # It only talks to the manager.
    # TODO: Call a method on the manager to get the day's lessons and print them.

# Feature 7 - Add New Course
def get_course_name():
    while True:
        course_name = input("Enter Course Name: ")
        try:
            if course_name.replace(" ","").isalpha() != True:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid name!\n")
    return course_name.lstrip().rstrip().title()

def get_course_instrument():
    while True:
        course_instrument = input("Enter Instrument: ")
        try:
            if course_instrument.replace(" ","").isalpha() != True:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid speciality!\n")
    return course_instrument.lstrip().rstrip().title()

# Feature 8 - Update Lesson Info
def get_course_venue(prompt):
    while True:
        user_input = input(prompt)
        return user_input.upper()

def get_course_note(prompt):
    while True:
        user_input = input(prompt)
        return user_input

def edit_lesson(course_id):
    # To create a new instance
    course_day = get_day("Enter day (e.g., Monday): ")
    course_venue = get_course_venue("Enter Venue: ")
    course_note = get_course_note("Enter Remark: ")
    new_lesson = {
        "Day": course_day,
        "Venue": course_venue,
        "Notes": course_note
    }
    # To load the lesson info for the course
    lesson_course = [c.lessons for c in manager.courses if c.id == course_id][0]
    lesson_course.append(new_lesson)
    print("----------")
    print(f"Course ID: {course_id}")
    print(f"Day: {new_lesson.get("Day")}")
    print(f"Venue: {new_lesson.get("Venue")}")
    print(f"Notes: {new_lesson.get("Notes")}")
    print("----------")
    action = confirm_action()
    if action:
        manager.save()
        return True

# Main function
def main():
    while True:
        print("\n===== MSMS v3 (Object-Oriented) =====")
        print("1 - Register New Student/Teacher")
        print("2 - Update Student/ Teacher")
        print("3 - Delete Student/ Teacher")
        print("4 - Check-in Student")
        print("5 - View Daily Roster")
        print("6 - View All")
        print("7 - Add New Course")
        print("8 - Update Lesson Info")
        print("q - Quit (Exit Key)")
        # To get user input
        choice = input("Enter choice: ")
        made_change = False
        # To match user input to different features
        match (choice):
            case "1":
                while True:
                    print("\n 1 - Student\n 2 - Teacher")
                    user = input("Enter [1/2]: ")
                    if user == "1" and check_course():
                        name, course= add_student()
                        manager.enroll_student(name, course)
                        made_change = True
                        break
                    elif user == "2":
                        name, speciality= add_teacher()
                        manager.enroll_teacher(name, speciality)
                        made_change = True
                        break
                    elif user == "q":
                        print("Changes not made.")
                        return main()
                    else:
                        print("Invalid Input!\nEnter q to exit")
            
            case "2":
                status = check_course()
                while status:
                    print("\n 1 - Student\n 2 - Teacher")
                    user = input("Enter [1/2]: ")
                    if user == "1":
                        print("\n--- Update New Student ---")
                        student_id = get_student_id()
                        from_course_id = get_course_id(" (From)")
                        to_course_id = get_course_id(" (To)")
                        action = switch_course(manager, student_id, from_course_id, to_course_id)
                        if action:
                            made_change = True
                            print("--------------------")
                            print("Successfully Updated!")
                            print([f"Name: {s.name}" for s in manager.students if s.id == int(student_id)][0])
                            print([f"Student ID: {student_id}" for s in manager.students if s.id == int(student_id)][0])
                            print([f"Courses: {s.enrolled_course_ids}" for s in manager.students if s.id == int(student_id)][0])
                            print("--------------------")
                            break
                    elif user == "2":
                        print("\n--- Update New Teacher ---")
                        teacher_id = get_teacher_id()
                        to_speciality = get_teacher_speciality()
                        action = update_teacher(teacher_id, to_speciality)
                        if action:
                            made_change = True
                            print("--------------------")
                            print("Successfully Updated!")
                            print([f"Name: {t.name}" for t in manager.teachers if t.id == int(teacher_id)][0])
                            print([f"Teacher ID: {t.id}" for t in manager.teachers if t.id == int(teacher_id)][0])
                            print([f"Speciality: {t.speciality}" for t in manager.teachers if t.id == int(teacher_id)][0])
                            print("--------------------")
                            break
                        break
                    elif user == "q":
                        print("Changes not made.")
                        return main()
                    else:
                        print("Invalid Input!\nEnter q to exit")
            
            case "3":
                while True:
                    print("\n 1 - Student\n 2 - Teacher")
                    user = input("Enter [1/2]: ")
                    if user == "1":
                        print("\n--- Delete Student ---")
                        student_id = get_student_id()
                        action = delete_student(student_id)
                        if action:
                            made_change = True
                    elif user == "2":
                        print("\n--- Delete Teacher ---")
                        teacher_id = get_teacher_id()
                        action = delete_teacher(teacher_id)
                        if action:
                            made_change = True
                    elif user == "q":
                        print("Changes not made.")
                        return main()
                    else:
                        print("Invalid Input!\nEnter q to exit")
            
            case "4":
                status = check_course()
                if status:
                    print("\n--- Check In Student ---")
                    student_id = get_student_id()
                    course_by_id = [s.enrolled_course_ids for s in manager.students if s.id == int(student_id)]
                    print(f"Courses under Student ID {student_id}: {course_by_id[0]}" + "\n")
                    course_id = get_course_id("")
                    if course_id in course_by_id[0]:
                        check_in(student_id, course_id)
                        made_change = True
                        for attendance in manager.attendance_log:
                            if attendance.get("Student ID") == int(student_id):
                                print("--------------------")
                                print("Successfully Checked In!")
                                print(f"Student ID: {attendance.get("Student ID")}")
                                print(f"Course ID: {attendance.get("Course ID")}")
                                print(f"Date/Time: {attendance.get("Timestamp")}")
                                print("--------------------")
                                break   
                    else:
                        print(f"Course '{course_id}' has not been enrolled by student ID '{student_id}' yet.")
                        print("Please try again.")
                        return main()

            case "5":
                print("\n--- View Daily Roaster ---")
                day = get_day("Enter day (e.g., Monday): ")
                print(f"Searching for lessons on {day}")
                front_desk_daily_roster(manager, day)

            case "6":
                while True:
                    print("\n 1 - Students\n 2 - Teachers\n 3 - Courses\n 4 - Attendance\n 5 - View All")
                    choice = input("Enter a number: ")
                    if choice not in ["1","2","3","4","5"]:
                        continue
                    if choice.isdigit() == True:
                        view_all_data(choice)
                        break

            case "7":
                print("\n--- Add New Course ---")
                course_id = get_course_id("new")
                course_name = get_course_name()
                course_instrument = get_course_instrument()
                course_teacher_id = get_teacher_id()
                manager.add_course(course_id, course_name, course_instrument, course_teacher_id)
                made_change = True

            case "8":
                print("\n--- Update Lesson Info ---")
                course_id = get_course_id("view")
                action = edit_lesson(course_id)
                if action:
                    manager.save()

            case "q":
                break
            case _:
                print("Invalid Input!")

        if made_change:
            manager.save()
        
if __name__ == "__main__":
    main()