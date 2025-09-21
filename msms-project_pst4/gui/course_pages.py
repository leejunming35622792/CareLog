# gui/course_pages.py
import streamlit as st
import datetime

def show_course_management_page(manager):
    all_teacher_id = [teacher.id for teacher in manager.teachers]
    # Renders all components for the student management page.
    st.header("Course Management")

    # Add new student
    st.subheader("Add New Course")
    with st.form("course_form"):
        # Get input to add new course
        new_course_name = st.text_input("Enter Course Name: ").title()
        new_course_instrument = st.text_input("Enter Instrument: ").title()

        teacher_option = {f"{t.id} - {t.name}": t.id for t in manager.teachers}
        new_course_teacher_id_list = st.selectbox("Choose Teacher ID: ", options=list(teacher_option.keys()))
        new_course_teacher_id = int(teacher_option[new_course_teacher_id_list])

        # Create submit button
        submitted = st.form_submit_button("Add Course")

        if submitted:
            if new_course_name and new_course_instrument and new_course_teacher_id:
                result = manager.add_course(new_course_name, new_course_instrument, new_course_teacher_id)

                if result:
                    manager.add_course(new_course_name, new_course_instrument, new_course_teacher_id)
                    st.success(f"Course '{new_course_name}' is successfully added under Course ID '{manager.next_lesson_id-1}'")
                    manager.save()
                else:
                    st.warning("Failed")
    
    st.subheader("Add Lesson")
    with st.form("lesson_form"):
        # 
        course_option = {f"{c.id} - {c.name}": c.id for c in manager.courses}
        course_lesson_list = st.selectbox("Select Course: ", list(course_option.keys()))
        course_lesson = int(course_option[course_lesson_list])

        # Create Input Box
        lesson_day = st.selectbox("Select Day: ", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        lesson_start_time = st.time_input("Enter Start Time: ")
        lesson_room = st.text_input("Enter Room: ").title()
        lesson_remark = st.text_input("Enter Remark (optional): ")

        # Create submit button
        submitted = st.form_submit_button("Add Lesson")

        # Check if all are filled in
        all_filled = course_lesson_list and lesson_day and lesson_start_time and lesson_room

        if submitted:
            if all_filled:
                result = manager.add_lesson(course_lesson, lesson_day, lesson_start_time, lesson_room, lesson_remark)
                if result:
                    st.success(f"""Successfully added \n   
                               Course: {course_lesson}\n   
                               Lesson ID: {manager.next_lesson_id-1}\n   
                               Lesson Day: {lesson_day}\n   
                               Start Time: {lesson_start_time}\n   
                               Room: {lesson_room}\n   
                               Remark: {lesson_remark}
                    """)
                    manager.save()
                else:
                    st.warning("Failed")
            else:
                st.warning("Please fill in the lesson details")
    
    st.subheader("Update Lesson")
    
        
    