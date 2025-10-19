import streamlit as st
import pandas as pd

# --- Sub-section: Course Data ---
def course_detail():
    tab1, tab2 = st.tabs(["Timetable", "Find Course & Lessons"])

    with tab1:
        # --- Roaster Section ---

        # Variable
        manager = st.session_state.manager
        username = st.session_state.username
        password = st.session_state.password
        current_student = next((s for s in manager.students if s.username == username), None)
        current_course = current_student.enrolled_course_ids
        all_lessons = []

        for c in manager.courses:
            for l in c.lessons:  # c.lessons is a list
                if isinstance(l, dict) and c.id in current_student.enrolled_course_ids:
                    all_lessons.append(l)
                elif hasattr(l, "__dict__"):  # handle Lesson objects
                    all_lessons.append(l.__dict__)

        st.subheader("Lessons Schedule:")

        # Define table structure
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        times = [f"{h:02d}:00" for h in range(9, 22)]  # 9AM–9PM

        schedule_df = pd.DataFrame(index=times, columns=days)
        schedule_df[:] = ""

        # Fill schedule grid
        for lesson in all_lessons:
            # Use dict-safe access
            day = lesson.get("day")
            time = lesson.get("start_time")[:5] if lesson.get("start_time") else ""
            room = lesson.get("room", "")
            remark = lesson.get("remark", "")

            if day in schedule_df.columns and time in schedule_df.index:
                schedule_df.loc[time, day] = f"{remark}\n({room})"

        # Style + display
        st.dataframe(
            schedule_df.style.set_properties(**{
                'text-align': 'center',
                'white-space': 'pre-wrap'
            }),
            use_container_width=True,
            height=500
        )
    
    with tab2:
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
            if course_disp:
                choose_course = course_disp[lesson_list]
            else:
                st.error("⚠️ Database is empty, no courses found")
            
            course_disp = next((c for c in manager.courses if c.id == choose_course), None)
                    
            all_lessons = manager.get_all_lessons(choose_course)

            if all_lessons:
                lesson_df = pd.DataFrame(all_lessons)
                lesson_pd_st = st.dataframe(lesson_df, hide_index=True)
            else:
                st.error("⚠️ Database is empty, no lessons found")

        st.divider()
        with st.container():
            st.subheader("Join for More Fun! 🥳")
        st.divider()
