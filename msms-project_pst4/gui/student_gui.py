import streamlit as st
import pandas as pd
import time
from app.schedule import ScheduleManager

# --- Sub-section: Dashboard ---
def dashboard():
    # Variable
    current_student = next((s for s in manager.students if s.username == current_username), None)

    # Dashboard Image
    st.image("C:/Users/Owner/FIT1056-Sem2-2025/msms-project_pst4/img/img1.jpg")

    # Metrix
    col1, col2 = st.columns(2)
    course_count = len(current_course)
    col1.metric(label="Courses Enrolled", value=course_count)
    attendance_count = len([a for a in manager.attendance_log if a.get("student_id") == current_student.id])
    col2.metric(label="Attendance Taken", value=attendance_count)

    # Personal Details
    st.divider()
    st.subheader("Who Are You? 👋")

    info = {
        "Username":current_student.username,
        "Password":current_student.password,
        "ID":current_student.id,
        "Name":current_student.name,
        "Courses":current_student.enrolled_course_ids
    }
    s_df = pd.DataFrame(list(info.items()), columns=["","Description"])
    st.dataframe(s_df, hide_index=True)

    # Courses
    st.divider()
    st.subheader("Your Teacher is Waiting For You 🏫")
    student_course = next((c.lessons for c in manager.courses if c.id in current_student.enrolled_course_ids), None)
    if student_course:
        s_df = pd.DataFrame(student_course)
        st.dataframe(s_df, hide_index=True)
    else:
        st.warning("Seemed like you haven't signed up any course 😥")

# --- Sub-section: Student Data ---
def student_detail():
    if "success_msg" in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg

    with st.form("update-student"):
        st.subheader("It's time to update... 🤔")
        st.info("To update a field, enter the new value and click 'Update'")

        # Update ID, name
        name = st.text_input("Update Name: ", value=current_student.name)
        instrument = st.text_input("Update Instrument: ", value=current_student.instrument)
        
        # Update Course
        course_disp = {f"{c.id} - {c.name}":c.id for c in manager.courses}
        id_to_label = {v: k for k, v in course_disp.items()}
        default_courses = [id_to_label[c_id] for c_id in current_course if c_id in id_to_label]
        courses_list = st.multiselect("Update Course: ", course_disp.keys(), default=default_courses)
        courses = [course_disp[c] for c in courses_list]

        # Update Credentials
        username = st.text_input("Update username: ", value=current_student.username)
        password = st.text_input("Update password: ", value=current_student.password, type="password")

        update_button = st.form_submit_button("Update Changes")

        if update_button:
            errors = []

            if username != current_username:
                if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                    errors.append("Username has been taken")
            if name:
                if not name.isalpha:
                    errors.append("Name cannot contain number or symbol!")
            if instrument:
                if not instrument.isalpha:
                    errors.append("Instrument cannot contain number or symbol!")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                result = manager.update_student(username, password, None, name.title(), instrument.title(), courses)
                
                if result:
                    with st.spinner("Saving...", show_time=True):
                        time.sleep(1)
                        manager.save()
                    st.balloons()                  
                    st.session_state.success_msg = "Successfully updated"
                    st.rerun()
                else:
                    st.error("Failed!")

# --- Sub-section: Course Data ---
def course_detail():
    # --- Find Course Section ---
    with st.container():
        st.subheader("All Available Courses")
        all_courses = [c.__dict__ for c in manager.courses]
        if all_courses:
            course_df = pd.DataFrame(all_courses)
            course_df = course_df.drop(columns=["enrolled_student_ids","lessons"])
            course_df.columns = course_df.columns.str.title()
            course_df_st = st.dataframe(course_df, hide_index=True)
        else:
            st.warning("⚠️ Database is empty, no courses found")
    st.divider()
    with st.container():
        st.subheader("Search Lessons by Course")
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        lesson_list = st.selectbox("Select Course: ", course_disp.keys())
        if lesson_list:
            choose_course = course_disp[lesson_list]
        else:
            st.error("⚠️ Database is empty, no courses found")
        
        all_lessons = []
        for c in manager.courses:
            if c.id == choose_course:
                for l in c.lessons:
                    all_lessons.append(l)
        lesson_df = pd.DataFrame(all_lessons)
        lesson_pd_st = st.dataframe(lesson_df, hide_index=True)
    st.divider()
    with st.container():
        st.subheader("Join for More Fun! 🥳")
    st.divider()

# --- Sub-section: Check In Attendance ---
def attendance():
    # --- Student Check-in Section ---
    st.subheader("Check-In Attendance")
    with st.form("check_in-form"):
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
                    st.balloons()
            else:
                st.error("Seemed like you haven't signed up any course 😥")

# --- Sub-section: Feedback ---
def feedback():
    with st.form("feedback-form"):
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses if current_student.id in c.enrolled_student_ids}

        if course_disp:
            choose_course = st.selectbox("Select Course", course_disp.keys())
        else:
            st.warning("⚠️ Database is empty, no courses found")
        
        like = st.feedback()

        st.text_area("Anything You Wish to Say:")

        submit = st.form_submit_button("Submit Feedback")
        
        if submit:
            st.write(like)

# --- Main Section---
def student_launch(Manager, username):
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    st.sidebar.title("MSMS Navigation")
    st.sidebar.write(f"@{username}")
    st.sidebar.divider()
    st.title("Music School Management System")

    global current_username
    current_username = username
    global manager
    manager = Manager
    global current_student
    current_student = next((s for s in manager.students if s.username == username), None)
    global current_course
    current_course = next((s.enrolled_course_ids for s in manager.students if s.username == username))

    page = st.sidebar.radio("Go to", ["Dashboard", "Personal", "Courses", "Attendance", "Feedback"])

    st.sidebar.divider()

    st.sidebar.button("Logout", on_click=logout)

    if page == "Dashboard":
        dashboard()
    elif page == "Personal":
        student_detail()
    elif page == "Courses":
        course_detail()
    elif page == "Attendance":
        attendance()
    elif page == "Feedback":
        feedback()

# --- Sub-section: Logout ---
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True