# FIT1056-Sem2-2025 PST1
# Lee Jun Ming 35622792

# --- Data Models ---
class Student:  #to create Student object
    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        self.enrolled_in = [] #to store students instruments

class Teacher:  #to create Teacher object
    def __init__(self, teacher_id, name, speciality):
        self.id = teacher_id
        self.name = name
        self.speciality = speciality

# --- In-Memory Databases ---
# to store students/teachers data
student_db = []
teacher_db = []

#starting of student/teacher id
next_student_id = 1
next_teacher_id = 1

admin_pw = "admin1234" #password to unlock system
staff_pw = "staff1234" #password access to view all students/teachers
name_found = False #used in find_students/find_teachers


# --- Core Helper Functions ---
#to add new students
def add_student():
    while True:
        #case handling
        try:
            name = input("Enter student name: ")

            checkName = name.replace(" ","")

            #check if input is all letters
            if checkName.isalpha () == False: 
                raise ValueError
            break

        except ValueError:
            print(f"Please enter a valid name!\n")
        
    while True:
        #case handling
        try:
            instrument = input("Enter instrument to enrol in: ")

            checkInstrument = instrument.replace(" ","")

            #check if input is all letters
            if checkInstrument.isalpha() != True: 
                raise ValueError
            break

        except ValueError:
            print(f"Please enter a valid instrument!\n")

    return name.title(), instrument.title() 
    #return name and instrument with first letter of every word in capital

#to add new teachers
def add_teacher(name, speciality):
    #global variable
    global next_teacher_id

    new_teacher = Teacher(next_teacher_id, name, speciality)
    
    #add new_teacher into teacher_db
    teacher_db.append(new_teacher)

    #ensure every id is distinct with increment of 1
    next_teacher_id += 1

    print(f"Core: Teacher '{name}' added successfully.")

#to list all students
def list_students():
    print("\n--- Student List ---")

    #if student_db has no element
    if not student_db:
        print("No students in the system.")
        return
    
    #loop student_db, and print every element in a particular format
    for student in student_db:
        print(f"  ID: {str(student.id).ljust(10)}, Name: {str(student.name).ljust(15)}, Enrolled in: {str(student.enrolled_in).ljust(10)}")

#to list all teachers
def list_teachers():
    print("\n--- Teacher List ---")

    #if teacher_db has no element
    if not student_db:
        print(f"No teachers in the system.")
        return

    #loop teacher_db, and print every element in a particular format
    for teacher in teacher_db:
        print(f"  ID: {str(teacher.id).ljust(10)}, Name: {str(teacher.name).ljust(15)}, Speciality: {str(teacher.speciality).ljust(10)}")

#to find student by name
def find_students(term):
    #variables
    global name_found
    current_name = []
    matched_student = None

    print(f"\n--- Finding Students matching '{term}' ---")

    #loop student_db
    for student in student_db:
        if term == student.name:               #if name is exactly found
            matched_student = student
        elif term in student.name.split():
            current_name.append(student.name)  #if similar name is found
    
    #for name that's exactly found
    if matched_student:
        #print
        print(f"ID: {matched_student.id}\nName: {matched_student.name}\nEnrolled in: {matched_student.enrolled_in}")

        #stop and exit this function
        name_found = True

    #similar names are found
    elif len(current_name) > 0:
        print(f"Possible Names: {current_name}")
        print(f"No exact match found.\n")

    else:
        print("No match found.\n")

#to find teacher by name and instrument
def find_teachers(term, speciality_check):
    #variables
    global name_found
    current_name = []
    matched_teacher = None
    matched_speciality = None

    print(f"\n--- Finding Teachers matching '{term}' ---")

    #loop teacher_db
    for teacher in teacher_db:
        #if name and speciality is exactly found
        if term == teacher.name and speciality_check == teacher.speciality:
            matched_teacher = teacher
            matched_speciality = speciality_check

        #if partially found
        elif term in teacher.name.split():
            current_name.append(teacher.name)
    
    #print if exatly found
    if matched_teacher and matched_speciality:
        #print
        print(f"ID: {matched_teacher.id}\nName: {matched_teacher.name}\nSpeciality: {matched_teacher.speciality}")

        #stop and exit this function
        name_found = True

    #name matches but speciality is wrong
    elif matched_teacher and speciality_check != matched_teacher.speciality:
        print(f"Incorrect speciality")

    #similar names are found
    elif len(current_name) > 0:
        print(f"Possible Names: {current_name}")
        print(f"No exact match found.\n")

    else:
        print("No match found.\n")


# --- Front Desk Functions ---
def find_student_by_id(student_id):
    #loop student_db
    #if ID matches student_id, return the student object.
    for student in student_db:
        if student.id == student_id:
            return student

    #return nothing if no record is found
    return None

#related to registration
def front_desk_register(name, instrument):
    #variables
    global next_student_id

    #create Student object, add to student_db, increment the ID.
    new_student = Student(next_student_id, name)
    student_db.append(new_student)
    next_student_id += 1
    
    #call front_desk_enrol() using the new student's ID and the provided instrument.
    front_desk_enrol(new_student.id, instrument)
    print(f"Front Desk: Successfully registered '{name}' and enrolled them in '{instrument}'.")

def front_desk_enrol(student_id, instrument):
    #Use find_student_by_id()
    student = find_student_by_id(student_id)

    #add the instrument to 'enrolled_in' list if found
    if student:
        student.enrolled_in.append(instrument)
        print(f"Front Desk: Enrolled student {student_id} in '{instrument}'.")

    else:
        #not found
        print(f"Error: Student ID {student_id} not found.")

#related to find students
def front_desk_lookup(term, speciality_check) :
    
    print(f"\n--- Performing lookup for '{term}' ---")

    #to add new student
    if len(speciality_check.split()) == 0:
        find_students(term)

    #user does enter speciality
    #to find teachers
    else:
        find_teachers(term.title(), speciality_check)


# --- Main Application ---
def main():
    while True:
        print("\n===== Music School Front Desk =====")
        print("1. Register New Student")
        print("2. Enrol Existing Student")
        print("3. Add New Teacher ")
        print("4. Lookup Student or Teacher")
        print("5. (Admin) List all Students")
        print("6. (Admin) List all Teachers")
        print("q. Quit")
        
        #user input to choose operation
        choice = input("Enter your choice: ")
        print()

        #register new student
        if choice == '1':
            #direct to add_student function to add new students
            name, instrument = add_student()
            front_desk_register(name, instrument)

        #enrol existing student
        elif choice == '2':
            # TODO: Prompt for student ID (as an int) and instrument, then call front_desk_enrol.
            try:
                student_id = int(input("Enter student ID: "))
                instrument = input("Enter instrument to enrol in: ")
                front_desk_enrol(student_id, instrument)
            except ValueError:
                print("Invalid ID. Please enter a number.")

        #add new teacher
        elif choice == "3":
            try:
                name = input("Enter teacher name: ")
                speciality = input("Enter speciality: ")
                current_teacher_name = name.replace(" ","")

                if current_teacher_name.alpha() == False:
                    raise ValueError
                
                if len(current_teacher_name) == 0:
                    raise ValueError
                
                add_teacher(name, speciality)

            except ValueError:
                print("Please enter a valid name and speciality!")

        #find student
        elif choice == '4':
            # TODO: Prompt for a search term, then call front_desk_lookup.
            while name_found == False:
                term = input("Enter search term (To exit, '999'): ")
                speciality_check = input("Enter speciality (if teacher): ").title()

                if term == "999":
                    print(f"Exit successfully")
                    break
                else:
                    front_desk_lookup(term, speciality_check) 

        #view all students
        elif choice == '5':
            trial = 1
            while True:
                pw_trial = input("Please enter staff password: ")

                if pw_trial == staff_pw:
                    list_students()
                    break

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

        #view all teachers
        elif choice == '6':
            trial = 1
            
            while True:
                pw_trial = input("Please enter staff password: ")

                if pw_trial == staff_pw:
                    list_teachers()
                    break

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

        #exit
        elif choice.lower() == 'q':
            print("Exiting program. Goodbye!")
            break

        #invalid input
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

    main()
