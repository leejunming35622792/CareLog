# gui/course_pages.py
import streamlit as st
import time
import pandas as pd
import logging

def show_course_management_page(manager):
    st.title("Course Management")
    
    if "success_msg" in st.session_state:
        st.balloons()
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg

    # Create different tabs
    tab_display = ["Find Course/Lessons", "Add Course", "Add Lesson", "Update Course", "Update Lesson", "Remove Course/Lesson"]
    find_course, add_course, add_lesson, update_course, update_lesson, remove = st.tabs(tab_display)

    # --- Find Course Section ---
    with find_course:
        st.subheader("View All Courses")
        with st.container():
            all_courses = [c.__dict__ for c in manager.courses]
            if all_courses:
                course_df = pd.DataFrame(all_courses)
                course_df = course_df.drop(columns=["lessons"])
                course_df.columns = course_df.columns.str.title()
                course_df_st = st.dataframe(course_df, hide_index=True)
            else:
                st.warning("⚠️ Database is empty, no courses found")

        st.divider()

        with st.container():
                st.subheader("Search Lessons by Course")

                course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
                lesson_list = st.selectbox("Select Course: ", course_disp.keys())
                if course_disp:
                    choose_course = course_disp[lesson_list]
                else:
                    st.error("⚠️ Database is empty, no courses found")
                        
                all_lessons = manager.get_all_lessons(choose_course)

                if all_lessons:
                    lesson_df = pd.DataFrame(all_lessons)
                    lesson_pd_st = st.dataframe(lesson_df, hide_index=True)
                else:
                    st.error("⚠️ Database is empty, no lessons found")

    # --- Add Course Section ---
    with add_course:
        st.subheader("Add New Course")
        with st.form("course_form"):
            # Get input to add new course
            new_course_name = st.text_input("Enter Course Name: ").title()
            new_course_instrument = st.text_input("Enter Instrument: ").title()

            teacher_option = {f"{t.id} - {t.name}": t.id for t in manager.teachers}
            new_course_teacher_id_list = st.selectbox("Choose Teacher ID: ", options=list(teacher_option.keys()))
            if new_course_teacher_id_list:
                new_course_teacher_id = teacher_option[new_course_teacher_id_list]
            else:
                st.error("⚠️ Database is empty, no courses found")

            # Create submit button
            submitted = st.form_submit_button("Add Course")

            if submitted:
                errors = []
                
                if not new_course_name:
                    errors.append("Course Name cannot be empty")
                if not new_course_instrument:
                    errors.append("Course Instrument cannot be empty")
                if not new_course_instrument.isalpha():
                    errors.append("Course Instrument cannot contain numbers or symbols")
                
                if errors:
                    for e in errors:
                        st.error(e)

                else:
                    result = manager.add_course(new_course_name, new_course_instrument, new_course_teacher_id)

                    if result:
                        with st.spinner("Saving...", show_time=True):
                            time.sleep(1)
                            manager.save()
                        st.session_state.success_msg = f"Course '{new_course_name}' is successfully added under Course ID '{manager.next_course_id-1}'"
                        logging.info(f"Add New Course {new_course_name}")
                        st.rerun()
                        
                    else:
                        st.warning("‼️ Failed, no changes detected.")
    
    # --- Add Lesson Section ---
    with add_lesson:
        st.subheader("Add Lesson")
        with st.form("lesson_form"):
            # Variable
            course_lesson = None

            # Create Input Box - Course
            course_option = {f"{c.id} - {c.name}": c.id for c in manager.courses}
            course_lesson_list = st.selectbox("Select Course: ", list(course_option.keys()))
            if course_lesson_list:
                course_lesson = course_option[course_lesson_list]
            else:
                st.error("⚠️ Database is empty, no course found")

            # Create input box
            lesson_day = st.selectbox("Select Day: ", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            lesson_start_time = st.time_input("Enter Start Time: ")
            lesson_room = st.text_input("Enter Room: ").upper()
            lesson_remark = st.text_input("Enter Remark (optional): ")

            # Create submit button
            submitted = st.form_submit_button("Add Lesson")

            if submitted:
                if not lesson_remark:
                    lesson_remark = course_lesson_list
                result = manager.add_lesson(course_lesson, lesson_day, lesson_start_time, lesson_room, lesson_remark)
                if result:
                    with st.spinner("Saving...", show_time=True):
                        time.sleep(1)
                        manager.save()
                    st.toast("Successfully added")
                    logging.info(f"Add Lesson for Course {course_lesson}")
                    st.rerun()
                else:
                    st.error("‼️ Failed, no changes found")
    
    # --- Update Course Section ---
    with update_course:
        st.subheader("Update Course")
        with st.form("update_course_form"):
            # Variable
            update_course_id = None

            st.info("To update, enter the new value for that particular field while leaving the others blank")

            # Get Updated Course ID
            courses_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
            course_chosen = st.selectbox("Select Course", courses_disp.keys())
            if course_chosen:
                update_course_id = courses_disp[course_chosen]
            else:
                st.error("⚠️ Database is empty, no courses found")

            # Get New Course Name
            update_name = st.text_input("Enter New Course Name: ").title()
            update_instrument = st.text_input("Enter New Instrument: ").title()

            # Get New Teacher ID
            teacher_id_disp = {f"{t.id} - {t.name}": t.id for t in manager.teachers}
            teacher_chosen = st.selectbox("Select New Teacher", teacher_id_disp.keys())
            update_teacher = teacher_id_disp[teacher_chosen]

            # Create button
            submitted = st.form_submit_button("Update Course")

            if submitted:
                errors = []
                
                if not new_course_name:
                    errors.append("Course Name cannot be empty")
                if not new_course_name.isalpha():
                    errors.append("Course Name cannot contain numbers or symbols")
                if not new_course_instrument:
                    errors.append("Course Instrument cannot be empty")
                if not new_course_instrument.isalpha():
                    errors.append("Course Instrument cannot contain numbers or symbols")
                
                if errors:
                    for e in errors:
                        st.error(e)

                else:
                    # Call update_course in ScheduleManager
                    update_course_button = manager.update_course(update_course_id, update_name, update_instrument, update_teacher)

                    if update_course_button:
                        manager.save()
                        updated_course = next((c for c in manager.courses if c.id == update_course_id))
                        st.success(f"""Successfully updated\n
                            Course ID: {updated_course.id}\n
                            Course Name: {updated_course.name}\n
                            Course Instrument: {updated_course.instrument}\n
                            Teacher ID: {updated_course.teacher_id}
                        """)
                        logging.info(f"Update Course {course_chosen}")
                    else:
                        st.warning("‼️ Failed, no changes detected")

    # --- Update Lesson Section ---
    with update_lesson:
        st.subheader("Update Lesson")
        with st.form("update-lesson"):
            # Variable
            lesson_map = {}
            update_lessonID = None

            st.info("To update, enter the new value for that particular field while leaving the others blank")

            for c in [c for c in manager.courses]:
                for l in c.lessons:
                    key = f"Course {c.id} '{c.name}' - Lesson {l['lesson-id']}"
                    lesson_map[key] = l["lesson-id"]

            lesson_chosen = st.selectbox("Select Lesson", list(lesson_map.keys()))
            
            if lesson_chosen:
                update_lessonID = lesson_map[lesson_chosen]
            else:
                st.error("⚠️ Database is empty, no lessons found")

            # Create input box
            update_day = st.selectbox("Enter New Day: ",["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            update_starttime = st.time_input("Enter New Start Time:")
            update_room = st.text_input("Enter New Room:")
            update_remark = st.text_input("Enter Remark:")

            # Create submit button
            update_lesson = st.form_submit_button("Update Changes")

            if update_lesson:
                # Call Update Lesson from ScheduleManager
                result = manager.update_lesson(update_lessonID, update_day, update_starttime, update_room, update_remark)

                if result:
                    st.success(f"""Successfully updated\n
                        Day: {update_day}\n
                        Start Time: {update_starttime}\n
                        Room: {update_room}\n
                        Remark: {update_remark}
                    """)
                    manager.save()
                    logging.info(f"Update Lesson for course {update_lessonID}")
                else:
                    st.warning("‼️ Failed, no changed detected")

    # --- Remove Section ---
    with remove:
        st.subheader("Delete Course Lesson")
        # Check delete course or lesson
        check_delete = st.selectbox("Delete...", ["Course", "Lesson"])

        # Variable
        delete_course_id = None
        delete_lessonID = None

        if check_delete == "Course":
            with st.form("delete-course-form"):
                course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses}
                course_chosen = st.selectbox("Select Course", course_disp.keys())
                if course_chosen:
                    delete_course_id = course_disp[course_chosen]

                # Create submit button
                delete_course_button = st.form_submit_button("Delete Course")

                # Create checkbox
                delete_course_checkbox = st.checkbox("By clicking confirm, I understand that deleting this student is permanent and cannot be undone.")

                if delete_course_button:
                    if delete_course_checkbox:
                        if delete_course_id:
                            result = manager.delete_course(delete_course_id)
                            if result:
                                logging.info(f"Remove Course {delete_course_id}")
                                st.success("Successfully deleted")
                            else:
                                st.error("‼️ Failed, no changes detected")
                        else:
                            st.error("⚠️ Database is empty, no courses found")
                    else:
                        st.warning("Please tick the checkbox to continue!")

        elif check_delete == "Lesson":
            lesson_map = {}

            for c in [c for c in manager.courses]:
                for l in c.lessons:
                    key = f"Course {c.id} - '{c.name}' - Lesson {l['lesson-id']} - Day {l['day']}"
                    lesson_map[key] = l["lesson-id"]
            
            if lesson_map == {}:
                st.error("⚠️ Database is empty, no lessons found")
                st.stop()
            else:
                with st.form("delete-form"):
                    lesson_chosen = st.selectbox("Select Lesson", list(lesson_map.keys()))
                    if lesson_chosen:
                        delete_lessonID = lesson_map[lesson_chosen]
                
                # Create submit button
                delete_lesson_button = st.form_submit_button("Delete Lesson")

                # Create checkbox
                delete_lesson_checkbox = st.checkbox("By clicking confirm, I understand that deleting this student is permanent and cannot be undone.")

                if delete_lesson_button:
                    if delete_lesson_checkbox:
                        if delete_lessonID:
                            result = manager.delete_lesson(delete_lessonID)
                            if result:
                                st.success("Successfully delete")
                            else:
                                st.error("‼️ Failed, no changes detected")
                        else:
                            st.error("⚠️ Database is empty, no lessons found")
                    else:
                        st.warning("Please tick the checkbox to continue!")
