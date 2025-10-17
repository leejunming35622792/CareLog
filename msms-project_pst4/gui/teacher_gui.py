import streamlit as st
import pandas as pd
import time
from app.schedule import ScheduleManager

# --- Sub-section: Dashboard ---
def dashboard():
    # Dashboard Image
    st.image("C:/Users/Owner/FIT1056-Sem2-2025/msms-project_pst4/img/img1.jpg")

    # Personal Details
    st.subheader("Who Are You?")

    current_teacher = next((t for t in manager.teachers if t.username == current_username), None)

    info = {
        "Username":current_teacher.username,
        "Password":current_teacher.password,
        "ID":current_teacher.id,
        "Name":current_teacher.name,
        "Speciality":current_teacher.speciality
    }
    t_df = pd.DataFrame(list(info.items()), columns=["","Description"])
    st.dataframe(t_df, hide_index=True)


    # Courses
    st.subheader("Your Student is Waiting For You")
    student_course = next((c.lessons for c in manager.courses if c.teacher_id == current_teacher.id), None)
    
    if student_course:
        s_df = pd.DataFrame(student_course)
        st.dataframe(s_df, hide_index=True)
    else:
        st.warning("Seemed like you aren't assigned to any course 😥")

# --- Sub-section: Teacher Data ---
def teacher_detail():
    if "success_msg" in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg

    with st.form("update-teacher"):
        st.info("To update a field, enter the new value and click 'Update'")

        # Update ID, name
        name = st.text_input("Update Name: ", value=current_teacher.name)
        speciality = st.text_input("Update Speciality: ", value=current_teacher.speciality)

        # Update Credentials
        username = st.text_input("Update username: ", value=current_username)
        password = st.text_input("Update password: ", value=current_teacher.password, type="password")

        update_button = st.form_submit_button("Update Changes")

        if update_button:
            errors = []

            if username != current_username:
                if username in [s.username for s in manager.students] or username in [t.username for t in manager.teachers]:
                    errors.append("Username has been taken")
            if name:
                if not name.isalpha:
                    errors.append("Name cannot contain number or symbol!")
            if speciality:
                if not speciality.isalpha:
                    errors.append("Speciality cannot contain number or symbol!")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                result = manager.update_teacher(username, password, None, name.title(), speciality.title())
                
                if result:
                    with st.spinner("Saving...", show_time=True):
                        time.sleep(1)
                        manager.save()                  
                    st.session_state.success_msg = "Successfully updated"
                    st.rerun()
                    
                else:
                    st.error("Failed!")

# --- Sub-section: Course Data ---
def course_detail():
    # --- Sub-section: View All Course ---
    with st.container():
        st.subheader("View All Courses")
        all_courses = [c.__dict__ for c in manager.courses]
        if all_courses:
            course_df = pd.DataFrame(all_courses)
            course_df = course_df.drop(columns=["enrolled_student_ids","lessons"])
            course_df.columns = course_df.columns.str.title()
            course_df_st = st.dataframe(course_df, hide_index=True)
        else:
            st.warning("⚠️ Database is empty, no courses found")

    # --- Sub-section: View Lessons ---
    with st.container():
        st.subheader("Search Lessons by Course")
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        lesson_list = st.selectbox("Select Course: ", course_disp.keys())
        if lesson_list:
            choose_course = course_disp[lesson_list]
            all_lessons = []
            for c in manager.courses:
                if c.id == choose_course:
                    for l in c.lessons:
                        all_lessons.append(l)
            lesson_df = pd.DataFrame(all_lessons)
            lesson_pd_st = st.dataframe(lesson_df, hide_index=True)
        else:
            st.warning("⚠️ Database is empty, no courses found")

# --- Main section ---
def teacher_launch(Manager, username):
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    st.sidebar.title("MSMS Navigation")
    st.sidebar.write(f"@{username}")
    st.sidebar.divider()
    st.title("Music School Management System")

    global manager
    manager = Manager
    global current_username
    current_username = username
    global current_teacher
    current_teacher = next((t for t in manager.teachers if t.username == username), None)

    page = st.sidebar.radio("Go to", ["Dashboard", "Personal", "Courses"])

    st.sidebar.divider()

    st.sidebar.button("Logout", on_click=logout)

    if page == "Dashboard":
        dashboard()
    elif page == "Personal":
        teacher_detail()
    elif page == "Courses":
        course_detail()

# --- Sub-section: Logout ---
def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True