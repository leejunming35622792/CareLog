# gui/roster_pages.py
import streamlit as st
import pandas as pd

def show_roster_page(manager):
    # --- Daily Roaster Section ---
    st.header("Daily Roster")
    with st.container():
        # Empty list to store lesson info at that day
        match_day = []

        # Choose a day
        day = st.selectbox("Select a day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

        # Loop to find lesson info
        for courses in [c for c in manager.courses]:
            for lesson in courses.lessons:
                if lesson["day"] == day:
                    match_day.append(lesson)
        
        # Convert to dataframe
        roaster_dataframe = pd.DataFrame(match_day)

        # Show the lesson info
        if match_day:
            st.dataframe(roaster_dataframe, hide_index=True)
        else:
            st.warning(f"No lessons found on {day}!")
    
    
    # --- Student Check-in Section ---
    st.subheader("Student Check-in")
    with st.container():
        # Get dict of student {name: ID}, display name, store ID
        student_list = {s.name: s.id for s in manager.students}
        selected_student_name = st.selectbox("Select Student", student_list.keys())
        student_id = student_list[selected_student_name]

        student_obj = next((s for s in manager.students if str(s.id) == str(student_id)), None)

        if student_obj:
            enrolled_course_ids = student_obj.enrolled_course_ids
            course_list = {c.name: c.id for c in manager.courses if c.id in enrolled_course_ids}
        else:
            course_list = {}

        with st.form("check_in_form"):
            # Check if the student enrols in any courses
            if course_list:
                selected_course_name = st.selectbox("Select Course", course_list.keys())

                # Create submit button
                submitted = st.form_submit_button("Check-in Student")

                if submitted:
                    # Convert the selected names back to IDs
                    course_id = course_list[selected_course_name]

                    # Call check in function in ScheduleManager()
                    success = manager.check_in(student_id, course_id)

                    if success:
                        st.success(f"Checked in '{selected_student_name}' for '{selected_course_name}'!")
                        manager.save()
                    else:
                        st.error("Check-in failed. See console for details. (Is the student enrolled in that course?)")
            else:
                st.warning(f"The student does not enroll in any course.")
