import streamlit as st
import pandas as pd
import json

def display_all_page(manager):
    st.header("Database")

    st.subheader("Students")
    students_cleaned = []
    for student in manager.students:
        students_cleaned.append({
            "Student Id": student.id,
            "Student Name": student.name,
            "Courses": student.enrolled_course_ids
        })
    students_df = pd.DataFrame(students_cleaned)
    st.dataframe(students_df, hide_index=True)

    st.subheader("Teachers")
    teachers_cleaned = []
    for teacher in manager.teachers:
        teachers_cleaned.append({
            "Teacher Id": teacher.id,
            "Teacher Name": teacher.name,
            "Speciality": teacher.speciality,
        })
    teachers_df = pd.DataFrame(teachers_cleaned)
    st.dataframe(teachers_df, hide_index=True)

    st.subheader("Courses")
    courses_cleaned = []
    for c in manager.courses:
        courses_cleaned.append({
            "Courses Id": c.id,
            "Course Name": c.name,
            "Instrument": c.instrument,
            "Teacher ID": c.teacher_id,
            "Enrolled Student IDs": c.enrolled_student_ids,
            "Lessons": [lesson for lesson in c.lessons]
        })
    courses_df = pd.DataFrame(courses_cleaned)
    st.dataframe(courses_df, hide_index=True)

    st.subheader("Attendance")
    attendance_cleaned = []
    for a in manager.attendance_log:
        attendance_cleaned.append({
            "student_id": a.get("student_id"),
            "course_id": a.get("course_id"),
            "timestamp": a.get("timestamp")
        })
    attendance_df = pd.DataFrame(attendance_cleaned)
    st.dataframe(attendance_df, hide_index=True)

    st.subheader("Show Json File")
    with st.form("show-json"):
        # Create button
        open_json = st.form_submit_button("Show / Hide Json File")

        # Load Json file
        with open("data/msms.json", "r") as f:
            data = json.load(f)

        # Initialize toggle state if not exists
        if "show_json" not in st.session_state:
            st.session_state.show_json = False

        # Toggle on button click
        if open_json:
            st.session_state.show_json = not st.session_state.show_json

        # Display JSON only if toggle is True
        if st.session_state.show_json:
            st.json(data, expanded=True)

