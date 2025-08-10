# FIT1056-Sem2-2025 PST1
# Lee Jun Ming 35622792

# --- Data Models ---
class Student:  #to create Student object
    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        self.enrolled_in = [] #to store students instruments

class Teacher:  # to create Teacher object
    def __init__(self, teacher_id, name, speciality):
        self.id = teacher_id
        self.name = name
        self.speciality = speciality

# --- In-Memory Databases ---
# to store students/teachers data
student_db = []
teacher_db = []

# starting of student/teacher id
next_student_id = 1
next_teacher_id = 1

admin_pw = "admin1234" # password to unlock system
staff_pw = "staff1234" # password access to view all students/teachers


# --- Core Helper Functions ---
# to add new students
def add_student():
    # variable
    all_name = []

    while True:
        # case handling
        try:
            # remove whitespace after words and capitalise every first letter
            name = input("Enter student name: ").rstrip().title()

            # remove all whitespaces
            checkName = name.replace(" ","")

            # check if input is all letters
            if checkName.isalpha () == False: 
                raise ValueError
            break

        except ValueError:
            print("Please enter a valid name!\n")
        
    while True:
        # case handling
        try:
            instrument = input("Enter instrument to enrol in: ").title()
            
            # remove all whitespaces
            checkInstrument = instrument.replace(" ","")

            # check if input is all letters
            if checkInstrument.isalpha() != True: 
                raise ValueError
            break

        except ValueError:
            print("Please enter a valid instrument!\n")

    # generate a list with all student names
    for student in student_db:
        all_name.append(student.name)

    if name in all_name:
        print(f"\nAlert - '{student.name}' with '{student.enrolled_in} has been recorded under ID '{student.id}' before.'") 

        print("1 - Add new student")
        print("2 - Exit and Enroll existing student")

        while True:
            proceed = input("Choose (1/2): ")

            if proceed == "1":
                # return name and instrument
                return name, instrument
        
            # return to main()
            elif proceed == "2":
                return main()

            else:
                print("Please enter 1 or 2 only.\n")

    else:
        return name, instrument
    
# to add new teachers
def add_teacher(name, speciality):
    # variable
    global next_teacher_id

    # generate a list of all teacher's name
    # to check whether a teacher has registered before
    all_name = [t.name for t in teacher_db]

    new_teacher = Teacher(next_teacher_id, name, speciality)

    # to check whether a teacher has registered before
    if name in all_name:
        print(f"Teacher '{name}' is already recorded under '{speciality}' speciality.")

        while True:
            print("1 - Add new teacher")
            print("2 - Change existing data")
            print("3 - Exit")
            proceed = input("Choose (1/2/3): ")

            # add new teacher
            if proceed == "1":
                teacher_db.append(new_teacher)
                next_teacher_id += 1
                print(f"Core: Teacher '{name}' with speciality '{speciality}' added successfully.")
                return 

            # change the existing data
            elif proceed == "2":
                for teacher in teacher_db:
                    if teacher.name == name:
                        teacher.speciality = speciality
                        print(f"Update '{teacher.name}' to speciality '{teacher.speciality}'.")
                return
            
            # return to main()
            elif proceed == "3":
                return

            else:
                print("Please enter 1, 2, or 3 only.")

    # add new teacher, increase id by 1
    teacher_db.append(new_teacher)
    next_teacher_id += 1
    print(f"Core: Teacher '{name}' with speciality '{speciality}' added successfully.")
    
# to list all students
def list_students():
    print("\n--- Student List ---")

    # if student_db has no element
    if not student_db:
        print("No students in the system.")
        return
    
    # loop student_db, and print every element in a particular format
    for student in student_db:
        print(f"  ID: {str(student.id).ljust(10)}, Name: {str(student.name).ljust(15)}, Enrolled in: {str(student.enrolled_in).ljust(10)}")

# to list all teachers
def list_teachers():
    print("\n--- Teacher List ---")

    # if teacher_db has no element
    if not student_db:
        print("No teachers in the system.")
        return

    # loop teacher_db, and print every element in a particular format
    for teacher in teacher_db:
        print(f"  ID: {str(teacher.id).ljust(10)}, Name: {str(teacher.name).ljust(15)}, Speciality: {str(teacher.speciality).ljust(10)}")

# to find student by name
# case sensitive
def find_students(term):
    # variable
    global name_found

    # generate a list of names that contain 'term'
    current_name = [s.name for s in student_db if term in s.name]

    print("\n--- Finding Students matching '{term}' ---")
    print("Alert - Case Sensitive!\n")

    # if the list doesnt contain the seach term
    if not current_name:
        print("No match found.\n")
        return 
    
    print("---- Possible Names ---")
        
    # find the names that are same with search term
    for student in student_db:
        for name in current_name:
            if student.name == name:
                print(f"ID: {student.id}\nName: {student.name}\nInstructions: {student.enrolled_in}\n")
                break
    
# to find teacher by name and instrument
# case insensitive
def find_teachers(term, speciality_check):
    # generate a list of names that contain search term
    matches = [t for t in teacher_db if term.lower() in t.name.lower()]

    print(f"\n--- Finding Teachers matching '{term}' ---")
    print(f"Alert - Case Insensitive!\n")

    # teacher is not found
    if not matches:
        print("No match found.\n")
        return

    found_exact = False

    for teacher in matches:
        # match teacher name and speciality
        if teacher.speciality.lower() == speciality_check.lower():
            print(f"ID: {teacher.id}\nName: {teacher.name}\nSpeciality: {teacher.speciality}\n")

            found_exact = True

        else:
            # name matched, but speciality different
            print(f"Do you mean...\nName: {teacher.name}\nSpeciality: {teacher.speciality}\n")

    if not found_exact:
        print("No exact speciality match found.\n")

# --- Front Desk Functions ---
# related to registration
def front_desk_register(name, instrument):
    # variable
    global next_student_id

    # create Student object, add to student_db, increment the ID.
    new_student = Student(next_student_id, name)
    student_db.append(new_student)
    next_student_id += 1
    
    # call front_desk_enrol() using the new student's ID and the provided instrument.
    front_desk_enrol(new_student.id, instrument)
    print(f"Front Desk: Successfully registered '{name}' and enrolled them in '{instrument}'.")

def find_student_by_id(student_id):
    # loop student_db
    # if ID matches student_id, return the student object.
    for student in student_db:
        if student.id == student_id:
            return student

    # return nothing if no record is found
    return None

def front_desk_enrol(student_id, instrument):
    # use find_student_by_id()
    student = find_student_by_id(student_id)

    # add the instrument to 'enrolled_in' list if found
    if student:
        student.enrolled_in.append(instrument)

        for student in student_db:
            if student.id == student_id:
                print(f"Front Desk: Enrolled student '{student.name}' in {student.enrolled_in}.")

    else:
        # not found
        print(f"Error: Student ID {student_id} not found.")

# related to find students
def front_desk_lookup(term, speciality_check) :
    
    print(f"\n--- Performing lookup for '{term}' ---")

    # to add new student
    if len(speciality_check.split()) == 0:
        find_students(term)

    # user does enter speciality
    # to find teachers
    else:
        find_teachers(term.title(), speciality_check.title())


# --- Main Application ---
def main(): 
    # used in find_students/find_teachers
    name_found = False

    while True:
        print("\n===== Music School Front Desk =====")
        print("1. Register New Student")
        print("2. Enroll Existing Student")
        print("3. Add New Teacher ")
        print("4. Lookup Student or Teacher")
        print("5. (Admin) List all Students")
        print("6. (Admin) List all Teachers")
        print("q. Quit")

        # user input to choose operation
        choice = input("Enter your choice: ")
        print()

        # register new student
        if choice == '1':
            # direct to add_student function to add new students
            name, instrument = add_student()
            front_desk_register(name, instrument)

        # enrol existing student
        elif choice == '2':
            try:
                student_id = int(input("Enter student ID: "))
                instrument = input("Enter instrument to enrol in: ").title()
                front_desk_enrol(student_id, instrument)
            except ValueError:
                print("Invalid ID. Please enter a number.")

        # add new teacher
        elif choice == "3":
            try:
                # get input for name & speciality, remove after-text whitespace, and capitalize every first letter
                name = input("Enter teacher name: ").rstrip().title()
                speciality = input("Enter speciality: ").rstrip().title()
                current_teacher_name = name.replace(" ","")

                #check if name includes number
                for letter in list(current_teacher_name):
                    if letter in [1,2,3,4,5,6,7,8,9,0,"!","@","#","$","%","^","*","?","<",">"]:
                        raise ValueError
                
                # if user enters nothing
                if len(current_teacher_name) == 0:
                    raise ValueError
                
                add_teacher(name, speciality)

            except ValueError:
                print("Please enter a valid name and speciality!")

        # find student/teacher
        elif choice == '4':
            while name_found == False:
                term = input("Enter search term (To exit, '999'): ")

                if term == "999":
                    print(f"Exit successfully")
                    break

                speciality_check = input("Enter speciality (if teacher): ").title()

                if not term:
                    print("Please enter a valid name (and speciality)\n")
                    continue

                front_desk_lookup(term, speciality_check)

        # view all students
        elif choice == '5':
            trial = 1
            while True:
                # only staff can access this feature
                pw_trial = input("Please enter staff password: ")

                # call list_student() if password is correct
                if pw_trial == staff_pw:
                    list_students()
                    break

                # lock the system when 3 incorrect password is entered
                if trial >= 3:
                    print("System locked!")

                    while True:
                        unlock_pw = input("Please enter admin password: ")

                        if unlock_pw == admin_pw:
                            return main()

                else:
                    print("Wrong password!")
                    print(f"{3-trial} trials left")
                    trial+=1

        # view all teachers
        elif choice == '6':
            trial = 1

            while True:
                # only staff can access this feature
                pw_trial = input("Please enter staff password: ")

                # call list_student() if password is correct
                if pw_trial == staff_pw:
                    list_teachers()
                    break

                # lock the system when 3 incorrect password is entered
                if trial == 3:
                    print("System locked!")

                    while True:
                        unlock_pw = input("Please enter admin password: ")

                        if unlock_pw == admin_pw:
                            return main()

                else:
                    print("Wrong password!")
                    print(f"{3-trial} trials left")
                    trial+=1

        # exit
        elif choice.lower() == 'q':
            print("Exiting program. Goodbye!")
            break

        # invalid input
        else:
            print("Invalid choice. Please try again.")

# --- Program Start ---
if __name__ == "__main__":
    # Pre-populate some data for easy testing
    add_teacher("Dr. Keys", "Piano")
    add_teacher("Ms. Fret", "Guitar")
    front_desk_register("Juan","Guitar")
    front_desk_register("John","Bass")
    front_desk_register("Aidan Chiang","Guitar")
    front_desk_register("Aidan Lim","Bass")

    # start the program
    main()
