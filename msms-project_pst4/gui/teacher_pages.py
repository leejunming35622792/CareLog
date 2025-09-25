# gui/student_pages.py
import streamlit as st
import pandas as pd
import time

def show_teacher_management_page(manager):
    st.header("Teacher Management")

    tab_display = ["Find Teacher", "Register Teacher", "Update Teacher", "Remove Teacher"]
    read, create, update, remove = st.tabs(tab_display)
    
    with read:
        # --- Search Section ---
        st.subheader("Find a Teacher")
        st.info("Search by name and press 'Enter'")
        with st.container():
            # Create input box
            search_keyword = st.text_input("Enter search keyword: ")

            # Call search_student in ManagerSchedule()
            match_teacher = manager.search_function("T", search_keyword)

            teacher_df = pd.DataFrame(match_teacher)
            st.dataframe(teacher_df, hide_index=True)

    with create:
        # --- Register Section ---
        st.subheader("Register New Teacher")
        with st.form("registration_form"):
            # Create Input Box
            reg_name = st.text_input("Enter Teacher Name: ").title()
            reg_speciality = st.text_input("Enter Speciality: ").title()

            # Create submit button
            submitted = st.form_submit_button("Register Teacher")
            
            # When user clicks submit button
            if submitted:
                errors = []
                # Check if both are inputted
                if not reg_name:
                    errors.append("Name cannot be empty")
                if not reg_speciality:
                    errors.append("Speciality cannot be empty")
                elif not reg_speciality.replace(" ", "").isalpha():
                    errors.append("Speciality cannot contain number or symbols")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    new_teacher = manager.enrolment("t", reg_name, reg_speciality, None)
                    if new_teacher:
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                        st.success(f"Successfully registered '{reg_name}' under ID '{manager.next_teacher_id - 1}'!")
                        manager.save()

                        st.balloons()
                    else:
                        st.error(f"Fail to register teacher {reg_name}!")

    with update: 
        # --- Update Section ---
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
                    # Pass to update function in manager
                    update_teacher = manager.update_teacher(update_id, update_name, update_speciality)

                    # Get updated info
                    updated_teacher = next((t for t in manager.teachers if str(t.id) == str(update_id)), None)

                    if update_teacher:
                        # Create delay
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                        st.success(f"""Successfully updated!\n
                            Name: {updated_teacher.name}\n
                            Speciality: {updated_teacher.speciality}\n
                        """)
                        manager.save()
                    else:
                        st.warning("Failed!")
                else:
                    st.warning(f"‼️ Failed, ID '{update_id}' is not found!")

    with remove:
        # --- Delete Section ---5
        st.subheader("Delete Teacher")
        with st.form("delete_teacher"):
            # Variable
            teacher_id = None

            # Create input box
            teacher_list = {f"{t.id} - {t.name}": t.id for t in manager.teachers}
            teacher_id_list = st.selectbox("Delete Teacher", teacher_list)
            if teacher_id_list:
                teacher_id = teacher_list[teacher_id_list]
            else:
                st.error("⚠️ Database is empty, no teachers found")

            # Create checkbox
            confirm_delete_checkbox = st.checkbox("By clicking confirm, I understand that deleting this teacher is permanent and cannot be undone.")

            # Create button
            check_delete = st.form_submit_button("Delete Teacher")

            # Button is first clicked
            if check_delete:
                if confirm_delete_checkbox:
                    delete = manager.remove_teacher(teacher_id)

                    if delete:
                        # Create delay
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                        st.success(f"Teacher ID '{teacher_id}' deleted successfully.")
                        manager.save()
                        st.session_state.show_confirm = False
                    else:
                            st.error("‼️ Failed, no changes detected")

                else:
                    st.error("Please tick the checkbox")