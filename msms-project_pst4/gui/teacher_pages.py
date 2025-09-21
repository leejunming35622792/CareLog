# gui/student_pages.py
import streamlit as st


def show_teacher_management_page(manager):
    # Renders all components for the teacher management page.
    st.header("Teacher Management")

    # --- Search Section (remains the same) ---
    st.subheader("Find a Teacher")
    pass
    # ...

    # Register Teacher
    st.subheader("Register New Teacher")
    with st.form("registration_form"):

        # Create Input Box
        reg_name = st.text_input("Enter Teacher Name: ").title()
        reg_speciality = st.text_input("Enter Speciality: ").title()

        # Create submit button
        submitted = st.form_submit_button("Register Teacher")
        
        # When user clicks submit button
        if submitted:
            # Check if both are inputted
            if reg_name and reg_speciality:
                new_teacher = manager.enrolment(reg_name, reg_speciality, None)
                if new_teacher:
                    st.success(f"Successfully registered '{reg_name}' under ID '{manager.next_teacher_id - 1}'!")
                    manager.save()
                else:
                    st.error(f"Fail to register teacher {reg_name}!")
            
            else:
                st.warning("Please enter both a name and a speciality.")
            
    # Update Teacher
    st.subheader("Update Teacher Info")
    with st.form("update_form"):
        # Variables
        all_teacher_ids = [teacher.id for teacher in manager.teachers]

        st.info("To update, enter the new value for that particular field while leaving the others blank")

        # Create input box
        update_id = st.text_input("Enter Teacher ID: ")
        update_name = st.text_input("Enter New Name: ", value = "").title()
        update_speciality = st.text_input("Enter New Speciality: ", value = "").title()
        
        # Create submit button
        submitted = st.form_submit_button("Save Update")
        
        # Case handling
        if submitted:

            # Check if ID exists
            if update_id in map(str, all_teacher_ids):
                # Find the dict of the particular teacher
                find_teacher_name = [t.name for t in manager.teachers if str(t.id) == update_id][0][0]
                find_teacher_speciality = [t.speciality for t in manager.teachers if str(t.id) == update_id][0][0]

                # Get default values for name & speciality
                if not update_name:
                    update_name = find_teacher_name
                if not update_speciality:
                    update_speciality = find_teacher_speciality

                # Pass to update function in manager
                update_teacher = manager.update_teacher(update_id, update_name, update_speciality)

                if update_teacher:
                    st.success("Successfully updated!")
                    manager.save()
                else:
                    st.warning("Failed!")
            else:
                st.warning(f"ID '{update_id}' is not found!")


