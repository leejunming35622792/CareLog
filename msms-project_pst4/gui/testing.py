import streamlit as st
import pandas as pd

def dashboard(manager):
    st.title("Welcome to MSMS v4")
    st.snow()

    st.info("This is MSMS, greeting you from the best Music Class Center, come and chat with us!")

    st.subheader("Students")
    students_cleaned = []
    for student in manager.students:
        students_cleaned.append({
            "Student ID": student.id,
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
