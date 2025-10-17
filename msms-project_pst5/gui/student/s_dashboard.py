import streamlit as st
import pandas as pd
from gui.teacher.t_dashboard import dashboard

# --- Sub-section: Dashboard ---
def dashboard():
    # Variable
    manager = st.session_state.manager
    username = st.session_state.username
    password = st.session_state.password
    current_student = next((s for s in manager.students if s.username == username), None)
    current_course = current_student.enrolled_course_ids

    # Dashboard Image
    st.image("C:/Users/Owner/FIT1056-Sem2-2025/msms-project_pst4/img/img1.jpg")
    st.divider()

    # Metrix
    col1, col2, col3, col4 = st.columns(4)
    course_count = len(current_course)
    col1.metric(label="ID", value=current_student.id)
    col2.metric(label="Name", value=current_student.name)
    col3.metric(label="Courses Enrolled", value=course_count)
    attendance_count = len([a for a in manager.attendance if a.get("student_id") == current_student.id])
    col4.metric(label="Attendance Taken", value=attendance_count)

    # Personal Details
    st.divider()
    st.header("Who Are You? 👋")

    info = {
        "Username":current_student.username,
        "Password":current_student.password,
        "ID":current_student.id,
        "Name":current_student.name,
        "Courses": ", ".join(current_student.enrolled_course_ids)
    }
    s_df = pd.DataFrame(list(info.items()), columns=["","Description"])
    st.dataframe(s_df, hide_index=True)

    # Courses
    st.divider()
    st.header("Your Teacher is Waiting For You 🏫")
    student_courses = manager.search_course_by_student_id(current_course)

    if student_courses:
        s_df = pd.DataFrame(student_courses)
        st.dataframe(s_df, hide_index=True)
    else:
        st.warning("Seemed like you haven't signed up any course 😥")