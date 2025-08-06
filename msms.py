#Fragment 1
# MSMS.py - The In-Memory Prototype

# --- Data Models ---
class Student:
    """A blueprint for student objects. Holds their info."""

    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        # TODO: Initialize an empty list called 'enrolled_in' to store instrument names.
        self.enrolled_in = []

class Teacher:
    """A blueprint for teacher objects."""
    
    def __init__(self, teacher_id, name, speciality):
        # TODO: Assign all three parameters (teacher_id, name, speciality)
        # to instance variables (e.g., self.id = teacher_id).
        self.id = teacher_id
        self.name = name
        self.speciality = speciality

# --- In-Memory Databases ---
# TODO: Create the global data stores.
student_db = []
teacher_db = []
next_student_id = 1
next_teacher_id = 1
name_found = False

#To Register
def register_new():
    while True:
        try:
            name = input("Enter student name: ")
            checkName = name.replace(" ","")
            if checkName.isalpha () == False:
                raise ValueError
            break
        except ValueError:
            print(f"Please enter a valid name!\n")
        
    while True:
        try:
            instrument = input("Enter instrument to enrol in: ")
            checkInstrument = instrument.replace(" ","")
            if checkInstrument.isalpha() != True:
                raise ValueError
            break
        except ValueError:
            print(f"Please enter a valid instrument!\n")

    return name.title(), instrument.title()


#Fragment 2
# --- Core Helper Functions ---
def add_teacher(name, speciality):
    """Creates a Teacher object and adds it to the database."""
    global next_teacher_id
    # TODO: Create a new Teacher object using the next available ID.
    new_teacher = Teacher(next_teacher_id, name, speciality)
    # TODO: Append the new_teacher to the teacher_db list.
    teacher_db.append(new_teacher)
    # TODO: Increment the next_teacher_id counter.
    next_teacher_id += 1
    print(f"Core: Teacher '{name}' added successfully.")

def list_students():
    """Prints all students in the database."""
    print("\n--- Student List ---")
    if not student_db:
        print("No students in the system.")
        return
    # TODO: Loop through student_db. For each student, print their ID, name, and their enrolled_in list.
    for student in student_db:
        print(f"  ID: {str(student.id).ljust(10)}, Name: {str(student.name).ljust(15)}, Enrolled in: {str(student.enrolled_in).ljust(10)}")

def list_teachers():
    """Prints all teachers in the database."""
    # TODO: Implement the logic to list all teachers, similar to list_students().
    print("\n--- Teacher List ---")
    for teacher in teacher_db:
        print(f"  ID: {str(teacher.id).ljust(10)}, Name: {str(teacher.name).ljust(15)}, Speciality: {str(teacher.speciality).ljust(10)}")

def find_students(term):
    global name_found
    current_name = []
    matched_student = None
    """Finds students by name."""

    print(f"\n--- Finding Students matching '{term}' ---")

    for student in student_db:
        if term == student.name:
            matched_student = student
        elif term in student.name.split():
            current_name.append(student.name)
    
    if matched_student:
        print(f"ID: {matched_student.id}\nName: {matched_student.name}\nEnrolled in: {matched_student.enrolled_in}")
        name_found = True

    elif len(current_name) > 0:
        print(f"Possible Names: {current_name}")
        print(f"No exact match found.\n")

    else:
        print("No match found.\n")

    # TODO: Create an empty list to store results.
    # Loop through student_db. If the search 'term' (case-insensitive) is in the student's name,
    # add them to your results list.
    # After the loop, if the results list is empty, print "No match found."
    # Otherwise, print the details for each student in the results list.

def find_teachers(term):
    global name_found
    current_name = []
    matched_teacher = None

    print(f"\n--- Finding Teachers matching '{term}' ---")

    for teacher in teacher_db:
        if term == teacher.name:
            matched_student = teacher
        elif term in teacher.name.split():
            current_name.append(teacher.name)
    
    if matched_student:
        print(f"ID: {matched_teacher.id}\nName: {matched_teacher.name}\nEnrolled in: {matched_teacher.speciality}")
        name_found = True

    elif len(current_name) > 0:
        print(f"Possible Names: {current_name}")
        print(f"No exact match found.\n")

    else:
        print("No match found.\n")

    """Finds teachers by name or speciality."""
    # TODO: Implement this function similar to find_students, but check
    # for the term in BOTH the teacher's name AND their speciality.

#Fragment 3
# --- Front Desk Functions ---
def find_student_by_id(student_id):
    """A new helper to find one student by their exact ID."""
    # TODO: Loop through student_db. If a student's ID matches student_id, return the student object.
    for student in student_db:
        if student.id == student_id:
            return student
    # TODO: If the loop finishes without finding a match, return None.
    return None

def front_desk_register(name, instrument):
    """High-level function to register a new student and enrol them."""
    global next_student_id
    # TODO: Create a new Student object, add it to student_db, and increment the ID.
    new_student = Student(next_student_id, name)
    student_db.append(new_student)
    next_student_id += 1
    
    # TODO: Immediately call front_desk_enrol() using the new student's ID and the provided instrument.
    front_desk_enrol(new_student.id, instrument)
    print(f"Front Desk: Successfully registered '{name}' and enrolled them in '{instrument}'.")

def front_desk_enrol(student_id, instrument):
    """High-level function to enrol an existing student in a course."""
    # TODO: Use your new find_student_by_id() helper.
    student = find_student_by_id(student_id)
    # TODO: If the student is found, append the instrument to their 'enrolled_in' list.
    if student:
        student.enrolled_in.append(instrument)
        print(f"Front Desk: Enrolled student {student_id} in '{instrument}'.")
    else:
        # TODO: If the student is not found, print an error message like "Error: Student ID not found."
        print(f"Error: Student ID {student_id} not found.")

def front_desk_lookup(term):
    """High-level function to search everything."""
    print(f"\n--- Performing lookup for '{term}' ---")
    find_students(term)
    find_teachers(term)


#Fragment 4
# --- Main Application ---
def main():
    """Runs the main interactive menu for the receptionist."""
    # Pre-populate some data for easy testing
    add_teacher("Dr. Keys", "Piano")
    add_teacher("Ms. Fret", "Guitar")
    front_desk_register("Juan","Guitar")
    front_desk_register("John","Bass")
    front_desk_register("Aidan Chiang","Guitar")
    front_desk_register("Aidan Lim","Bass")

    while True:
        print("\n===== Music School Front Desk =====")
        print("1. Register New Student")
        print("2. Enrol Existing Student")
        print("3. Lookup Student or Teacher")
        print("4. (Admin) List all Students")
        print("5. (Admin) List all Teachers")
        print("q. Quit")
        
        choice = input("Enter your choice: ")
        print()

        if choice == '1':
            # TODO: Prompt for student name and instrument, then call front_desk_register.
            name, instrument = register_new()
            front_desk_register(name, instrument)

        elif choice == '2':
            # TODO: Prompt for student ID (as an int) and instrument, then call front_desk_enrol.
            try:
                student_id = int(input("Enter student ID: "))
                instrument = input("Enter instrument to enrol in: ")
                front_desk_enrol(student_id, instrument)
            except ValueError:
                print("Invalid ID. Please enter a number.")

        elif choice == '3':
            # TODO: Prompt for a search term, then call front_desk_lookup.
            while name_found == False:
                term = input("Enter search term (To exit, '999'): ").title()
                if term == "999":
                    print(f"Exit successfully")
                    break
                else:
                    front_desk_lookup(term) 

        elif choice == '4':
            list_students()

        elif choice == '5':
            list_teachers()

        elif choice.lower() == 'q':
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

# --- Program Start ---
if __name__ == "__main__":
    main()