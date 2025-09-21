# gui/student_pages.py
import streamlit as st

def show_student_management_page(manager):
    # Renders all components for the student management page.
    st.header("Student Management")

    # --- Search Section ---
    st.subheader("Find a Student")
    pass
    # ...

    # --- Add Student Section ---
    st.subheader("Register New Student")
    with st.form("registration_form"):

        # Create input boxs
        reg_name = st.text_input("Enter Student Name: ").title()
        reg_instrument = st.text_input("Enter First Instrument: ").title()

        # Create a dict to display
        course_options = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        reg_course_labels = st.multiselect("Select All Courses: ", options=list(course_options.keys()))
        reg_course = [course_options[label] for label in reg_course_labels]

        # Create submit button
        submitted = st.form_submit_button("Register Student")

        # If button is clicked
        if submitted:
            if reg_name and reg_instrument:
                new_student = manager.enrolment(reg_name, reg_instrument, reg_course)
                if new_student:
                    st.success(f"Successfully registered '{reg_name}' under ID '{manager.next_student_id}'!")
                    manager.save()
                    # You can use st.balloons() for extra flair.
            else:
                st.warning("Please enter both a name and an instrument.")

    # --- Update Student Info Section ---
    st.subheader("Update Student Info")
    with st.form("update_form"):
        # Variable
        all_student_ids = [s.id for s in manager.students]

        st.info("To update, enter the new value for that particular field while leaving the others blank")

        # Create input box
        update_id = st.text_input("Enter Student ID: ").title()
        update_name = st.text_input("Enter New Name: ").title()

        # Create a dict to display
        course_option = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        update_course_labels = st.multiselect("Select All Courses: ", options=list(course_option.keys()))
        update_course = [course_option[label] for label in update_course_labels]

        # Create submit button
        submitted = st.form_submit_button("Save Update")

        if submitted:
            
            # Make copy of original info
            ori_name = next((s.name for s in manager.students if str(s.id) == update_id), None)
            ori_course = next((s.enrolled_course_ids for s in manager.students if str(s.id) == update_id), None)

            # Check if the ID exists
            if update_id in map(str, all_student_ids):
                # Find the dict of the particular student
                find_student_name = next((s.name for s in manager.students if str(s.id) == update_id), None)
                find_student_course = next((s.enrolled_course_ids for s in manager.students if str(s.id) == update_id), None).sort()

                # Fill the default values of name and course
                if not update_name:
                    update_name = find_student_name
                if not update_course:
                    update_course = find_student_course

                update_student = manager.update_student(update_id, update_name, update_course)

                if update_student:
                    st.success(f"""Successfully updated!\n
                                Name: {ori_name} -> {update_name}\n
                                Course: {ori_course} -> {update_course}
                               """)
                    manager.save()
                else:
                    st.warning("Failed")  

            else:
                st.warning(f"ID '{update_id}' is not found!")
    
    # --- Delete Section ---