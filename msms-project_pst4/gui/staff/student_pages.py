# gui/student_pages.py
import streamlit as st
import pandas as pd
import time

def show_student_management_page(manager):
    # Renders all components for the student management page.
    st.header("Student Management")

    # Create different tabs
    tab_display = ["Find Student", "Register Student", "Update Student", "Remove Student"]
    read, create, update, remove = st.tabs(tab_display)

    if "success_msg" in st.session_state:
        st.balloons()
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg

    with read:
        # --- Search Section ---
        st.subheader("Find a Student")
        st.info("Search by name and press 'Enter'")
        with st.container():
            # Create input box
            search_keyword = st.text_input("Enter search keyword: ")

            # Call search_student in ManagerSchedule()
            match_student = manager.search_function("S", search_keyword)

            student_df = pd.DataFrame(match_student)
            st.dataframe(student_df, hide_index=True)

    with create:
        # --- Add Student Section ---
        st.subheader("Register New Student")
        with st.form("registration_form"):
            # Create input boxs
            username = st.text_input("Enter Username: ", key="input_username")
            password = st.text_input("Enter Password: ", key="input_password",type="password")
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
                errors = []
                if not username:
                    errors.append("Username cannot be empty!")
                if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                        errors.append("Username has been taken!")
                if not password:
                    errors.append("Password cannot be empty!")
                if not reg_name:
                    errors.append("Name cannot be empty!")
                if not reg_name.replace(" ","").isalpha():
                    errors.append("Name cannot contain numbers or symbols!")
                if len(reg_instrument) == 0:
                    errors.append("Enter None if you haven't learnt any instrument!")
                elif not reg_instrument.replace(" ", "").isalpha():
                    errors.append("Instrument cannot contain numbers or symbols!")
                if not reg_course:
                    errors.append("Please select at least one course!")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    new_student = manager.enrolment("s", username, password, reg_name, reg_instrument, reg_course)
                    if new_student:
                        # Add delay time
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(1)
                        manager.save()
                        st.session_state.success_msg = f"Successfully registered '{reg_name}' under ID '{manager.next_student_id-1}'!"
                        st.rerun()
                        
                    else:
                        st.warning("⚠️ Failed, no changes detected")

    with update:
        # --- Update Student Info Section ---
        st.subheader("Update Student Info")
        with st.form("update_form"):
            # Variable
            all_student_ids = [s.id for s in manager.students]

            st.info("To update, enter the new value for that particular field while leaving the others blank")

            # Get updated ID
            id_disp = {f"{s.id} - {s.name}": s.id for s in manager.students}
            update_id_list = st.selectbox("Enter Student ID: ", id_disp.keys())
            if update_id_list:
                update_id = id_disp[update_id_list]

                # Get updated name
                update_name = st.text_input("Enter New Name: ").title()

                update_instrument = st.text_input("Enter New Instrument: ").title()

                # Get updated course
                course_option = {f"{c.id} - {c.name}": c.id for c in manager.courses}
                update_course_labels = st.multiselect("Select All Courses: ", options=course_option.keys())

            else:
                st.error("⚠️ Database is empty, no students found")

            # Create submit button
            submitted = st.form_submit_button("Save Update")

            if submitted:
                if update_id_list:
                    errors = []

                    if not update_course_labels:
                        update_course_labels = []

                    if errors:  
                        for e in errors:
                            st.error(e)
                        
                    else:
                        update_course = [course_option[c] for c in update_course_labels]

                        # Call update_student in ManagerSchedule
                        update_student = manager.update_student(None, None, update_id, update_name, update_instrument, update_course)

                        if update_student:
                            # Create delay
                            with st.spinner("Saving...", show_time=True):
                                time.sleep(1)
                            st.session_state.success_msg = True
                            manager.save()

                            # Get updated details
                            updated_student = next((s for s in manager.students if str(s.id) == str(update_id)), None)

                            st.session_state.success_msg = f"""Successfully updated!\n
                                ID: {updated_student.id}\n
                                Name: {updated_student.name}\n
                                Course: {updated_student.enrolled_course_ids}
                                    """
                            st.rerun()
                        else:
                            st.error("‼️ Failed, no changes detected")  
                            
                else:
                    st.error("‼️ Failed, no changes detected")

    with remove:
        # --- Delete Section ---
        st.subheader("Delete Student")
        with st.form("delete_student"):
            # Variable
            student_id = 0

            # Create input box
            student_list = {f"{s.id} - {s.name}": s.id for s in manager.students}
            student_id_list = st.selectbox("Select Student", student_list.keys())

            if student_id_list:
                student_id = student_list[student_id_list]
            else:
                st.error("⚠️ Database is empty, no students found.")

            # Create button
            check_delete = st.form_submit_button("Delete Student")

            if "show_confirm" not in st.session_state:
                st.session_state.show_confirm = False

            # Button is first clicked
            if check_delete:
                if student_id_list:
                    st.warning("Are you sure you want to delete this student?")
                    # Store state
                    st.session_state.show_confirm = True
                else:
                    st.error("‼️ Failed, no students found")

            if st.session_state.show_confirm:
                confirm_delete = st.form_submit_button("Confirm Delete")
                if confirm_delete:
                    delete = manager.remove_student(student_id)

                    if delete:
                        # Create delay
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                        manager.save()
                        st.session_state.success_msg = f"Student ID '{student_id}' deleted successfully."
                        st.rerun()
                        
                    else:
                        st.error("‼️ Failed, no changes detected")