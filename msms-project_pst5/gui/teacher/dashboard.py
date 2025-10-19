import streamlit as st
import pandas as pd

def dashboard(manager):
    st.snow()

    st.info("This is MSMS, greeting you from the best Music Class Center, come and chat with us!")

    st.subheader("Overview:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Students",value=len(manager.students))
    col2.metric(label="Teachers",value=len(manager.teachers))
    col3.metric(label="Courses",value=len(manager.courses))
    col4.metric(label="Lessons",value=len([l for c in manager.courses for l in c.lessons]))

    st.divider()
    st.subheader("Students:")
    students_cleaned = []
    for student in manager.students:
        students_cleaned.append({
            "Student ID": student.id,
            "Student Name": student.name,
            "Courses": student.enrolled_course_ids
        })
    if students_cleaned:
        students_df = pd.DataFrame(students_cleaned)
        st.dataframe(students_df, hide_index=True)
    else:
        st.warning("⚠️ No Students!")

    st.subheader("Teachers:")
    teachers_cleaned = []
    for teacher in manager.teachers:
        teachers_cleaned.append({
            "Teacher ID": teacher.id,
            "Teacher Name": teacher.name,
            "Speciality": teacher.speciality,
        })
    if teachers_cleaned:
        teachers_df = pd.DataFrame(teachers_cleaned)
        st.dataframe(teachers_df, hide_index=True)
    else:
        st.warning("⚠️ No Teachers!")

    st.subheader("Courses:")
    courses_cleaned = []
    for c in manager.courses:
        courses_cleaned.append({
            "Courses Id": c.id,
            "Course Name": c.name,
            "Instrument": c.instrument,
            "Teacher ID": c.teacher_id,
            "Enrolled Student IDs": c.enrolled_student_ids,
            "Lessons": [lesson.get("lesson-id") for lesson in c.lessons]
        })
    if courses_cleaned:
        courses_df = pd.DataFrame(courses_cleaned)
        st.dataframe(courses_df, hide_index=True)
    else:
        st.warning("⚠️ No Courses!")