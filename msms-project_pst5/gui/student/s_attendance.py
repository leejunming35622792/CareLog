import streamlit as st
import logging

# --- Sub-section: Check In Attendance ---
def attendance():
    # Variable
    manager = st.session_state.manager
    username = st.session_state.username
    password = st.session_state.password
    current_student = next((s for s in manager.students if s.username == username), None)
    current_course = current_student.enrolled_course_ids

    # --- Student Check-in Section ---
    with st.form("check_in-form"):
        st.header("Check-In Attendance")
        st.info("Select the course ID to check-in attendance.")
        st.divider()
        
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses if c.id in current_course}
        if course_disp:
            choosen_course = st.selectbox("Select Course", course_disp.keys())
        else:
            st.warning("No Courses Found!")
            
        # Create submit button
        submitted = st.form_submit_button("Check-in ✅")

        if submitted:
            if course_disp:
                # Convert the selected names back to IDs
                course_id = course_disp[choosen_course]

                # Call check in function in ScheduleManager()
                success = manager.check_in(current_student.id, course_id)

                if success:
                    st.success(f"Checked in '{current_student.name}' for '{choosen_course}'!")
                    manager.save()
                    st.session_state.backup = "backup"
                    logging.info(f"Check in Attendance - {course_id}")
                    st.balloons()
            else:
                st.error("Seemed like you haven't signed up any course 😥")
