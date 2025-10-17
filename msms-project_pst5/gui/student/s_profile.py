import streamlit as st
import time
import logging

# --- Sub-section: Student Data ---
def profile():
    # Variable
    manager = st.session_state.manager
    username = st.session_state.username
    password = st.session_state.password
    current_student = next((s for s in manager.students if s.username == username), None)
    current_course = current_student.enrolled_course_ids

    with st.form("update-student"):
        st.header("Student Profile")
        st.write("It's time to update... 🤔")
        st.info("To update a field, enter the new value and click 'Update'")
        st.divider()

        # Update ID, name
        name = st.text_input("Update Name: ", placeholder=current_student.name)
        instrument = st.text_input("Update Instrument: ", placeholder=current_student.instrument)
        
        # Update Course
        course_disp = {f"{c.id} - {c.name}":c.id for c in manager.courses}
        id_to_label = {v: k for k, v in course_disp.items()}
        default_courses = [id_to_label[c_id] for c_id in current_course if c_id in id_to_label]
        courses_list = st.multiselect("Update Course: ", course_disp.keys(), default=default_courses)
        courses = [course_disp[c] for c in courses_list]

        # Update Credentials
        updated_username = st.text_input("Update username: ", value=current_student.username)
        updated_password = st.text_input("Update password: ", value=current_student.password, type="password")

        update_button = st.form_submit_button("Update Changes")

        if update_button:
            errors = []
            success = []

            if updated_username != username:
                if updated_username in [s.username for s in manager.students] or updated_username in [t.username for t in manager.teachers]:
                    errors.append("Username has been taken")
                success.append("Username")
            if password:
                success.append("Password")
            if name:
                if not name.isalpha:
                    errors.append("Name cannot contain number or symbol!")
                success.append("Name")
            if instrument:
                if not instrument.isalpha:
                    errors.append("Instrument cannot contain number or symbol!")
                success.append("Instrument")
            if courses:
                success.append("Courses")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                result = manager.update_student(updated_username, updated_password, None, name.title(), instrument.title(), courses)
                
                if result:
                    with st.spinner("Saving...", show_time=True):
                        time.sleep(1)
                        manager.save()
                    st.balloons()                  
                    st.session_state.success_msg = f"Successfully Updated - {", ".join(success)}"
                    st.session_state.backup = "backup"
                    logging.info(f"Successfully Updated - {", ".join(success)}")
                    st.rerun()
                else:
                    st.error("Failed!")

    if "success_msg" in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg