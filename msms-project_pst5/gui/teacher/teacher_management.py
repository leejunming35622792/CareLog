# gui/student_pages.py
import streamlit as st
import pandas as pd
import time
import logging

def show_teacher_management_page(manager):
    st.header("Teacher Management")

    tab_display = ["Find Teacher", "Register Teacher", "Update Teacher", "Remove Teacher"]
    read, create, update, remove = st.tabs(tab_display)

    if "success_msg" in st.session_state:
        st.balloons()
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg
    
    with read:
        # --- Search Section ---
        st.subheader("Find a Teacher")
        st.info("Search by name and press 'Enter'")
        with st.container():
            # Create input box
            search_keyword = st.text_input("Enter search keyword: ")

            # Call search_student in ManagerSchedule()
            match_teacher = manager.search_function("T", search_keyword)

            if match_teacher:
                teacher_df = pd.DataFrame(match_teacher)
                st.dataframe(teacher_df, hide_index=True)
            else:
                st.error("⚠️ Database is empty, no teachers found")

    with create:
        # --- Register Section ---
        st.subheader("Register New Teacher")
        with st.form("registration_form"):
            # Create input boxs
            username = st.text_input("Enter Username: ", key="input_username")
            password = st.text_input("Enter Password: ", key="input_password",type="password")
            reg_name = st.text_input("Enter Teacher Name: ").title()
            reg_speciality = st.text_input("Enter Speciality: ").title()

            # Create submit button
            submitted = st.form_submit_button("Register Teacher")
            
            # When user clicks submit button
            if submitted:
                errors = []
                if not username:
                    errors.append("Username cannot be empty!")
                if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                        errors.append("Username has been taken!")
                if not password:
                    errors.append("Password cannot be empty!")
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
                    new_teacher = manager.enrolment("t", username, password, reg_name, reg_speciality, None)
                    if new_teacher:
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                            manager.save()
                        st.session_state.success_msg = f"Successfully registered '{reg_name}' under ID '{manager.next_teacher_id - 1}'!"
                        st.rerun()
                        logging.info(f"Register New Teacher @{username}")
                        st.balloons()
                    else:
                        st.error(f"Fail to register teacher {reg_name}!")

    with update: 
        # --- Update Section ---
        st.subheader("Update Teacher Info")
        with st.form("update_form"):
            # Variable
            all_teacher_ids = [teacher.id for teacher in manager.teachers]

            st.info("To update, enter the new value for that particular field while leaving the others blank")

            # Create input box
            teacher_disp = {f"{t.id} - {t.name}": t.id for t in manager.teachers}
            if teacher_disp:
                update_id_list = st.selectbox("Enter Teacher ID: ",teacher_disp.keys())
                update_id = teacher_disp[update_id_list]
            else:
                st.error("⚠️ Database is empty, no teachers found")

            username = st.text_input("Enter Username: ")
            password = st.text_input("Enter Password: ")
            update_name = st.text_input("Enter New Name: ", value = "").title()
            update_speciality = st.text_input("Enter New Speciality: ", value = "").title()

            # Create submit button
            submitted = st.form_submit_button("Save Update")
            
            # Case handling
            if submitted:
                # Check if ID exists
                if update_id in all_teacher_ids:
                    # Pass to update function in manager
                    update_teacher = manager.update_teacher(username, password, update_id, update_name, update_speciality)

                    # Get updated info
                    updated_teacher = next((t for t in manager.teachers if str(t.id) == str(update_id)), None)

                    if update_teacher:
                        # Create delay
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(3)
                            manager.save()
                        st.session_state.success_state = f"Successfully updated!"
                        logging.info(f"Update Teacher @{username} Profile")
                        st.rerun()
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
                            manager.save()
                        st.session_state.success_msg = f"Teacher ID '{teacher_id}' deleted successfully."
                        st.session_state.show_confirm = False
                        logging.info(f"Remove Teacher @{username}")
                        st.rerun()
                    else:
                            st.error("‼️ Failed, no changes detected")

                else:
                    st.error("Please tick the checkbox")