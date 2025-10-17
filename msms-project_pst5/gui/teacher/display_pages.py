import streamlit as st
import pandas as pd
import json
import os

def display_all_page(manager):
    # Page title
    st.title("MSMS Database")

    # Create tabs for organizing content
    tab1, tab2, tab3 = st.tabs(["Basic Dataframe", "Log Viewer", "JSON"])

    # ---------------------------- TAB 1: BASIC DATAFRAME ----------------------------
    with tab1:
        # ---------------- STUDENTS SECTION ----------------
        st.subheader("Students")
        students_cleaned = []
        # Convert student objects into a list of dictionaries
        for student in manager.students:
            students_cleaned.append({
                "Student ID": student.id,
                "Student Name": student.name,
                "Courses": student.enrolled_course_ids
            })
        # Create a DataFrame for visualization
        students_df = pd.DataFrame(students_cleaned)
        st.dataframe(students_df, hide_index=True)
        
        st.divider()
        
        # ---------------- TEACHERS SECTION ----------------
        st.subheader("Teachers")
        teachers_cleaned = []
        # Convert teacher objects into a list of dictionaries
        for teacher in manager.teachers:
            teachers_cleaned.append({
                "Teacher Id": teacher.id,
                "Teacher Name": teacher.name,
                "Speciality": teacher.speciality,
            })
        # Create and display DataFrame
        teachers_df = pd.DataFrame(teachers_cleaned)
        st.dataframe(teachers_df, hide_index=True)

        st.divider()

        # ---------------- COURSES SECTION ----------------
        st.subheader("Courses")
        courses_cleaned = []
        # Extract relevant course details and lessons
        for c in manager.courses:
            courses_cleaned.append({
                "Courses Id": c.id,
                "Course Name": c.name,
                "Instrument": c.instrument,
                "Teacher ID": c.teacher_id,
                "Enrolled Student IDs": c.enrolled_student_ids,
                "Lessons": [lesson for lesson in c.lessons]
            })
        # Display all course data
        courses_df = pd.DataFrame(courses_cleaned)
        st.dataframe(courses_df, hide_index=True)

        st.divider()

        # ---------------- ATTENDANCE SECTION ----------------
        st.subheader("Attendance")
        attendance_cleaned = []
        # Extract attendance records
        for a in manager.attendance:
            attendance_cleaned.append({
                "student_id": a.get("student_id"),
                "course_id": a.get("course_id"),
                "timestamp": a.get("timestamp")
            })
        # Display attendance table
        attendance_df = pd.DataFrame(attendance_cleaned)
        st.dataframe(attendance_df, hide_index=True)

        st.divider()

    # ---------------------------- TAB 2: LOG VIEWER ----------------------------
    with tab2:
        st.subheader("Download Logs")
        BASE_DIR = "data/logs"

        # Step 1: Get list of user directories inside /data/logs
        users = [u for u in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, u))]

        if not users:
            st.error("No log folders found.")
        else:
            # User selection dropdown
            selected_user = st.selectbox("Select a user:", users)

            if selected_user:
                user_dir = os.path.join(BASE_DIR, selected_user)

                # Step 2: Get all .log files for the selected user
                log_files = [f for f in os.listdir(user_dir) if f.endswith(".log")]
                log_files.sort(reverse=True)

                if not log_files:
                    st.warning("No log files found for this user.")
                else:
                    # Select specific log file
                    selected_log = st.selectbox("Select a log file:", log_files)

                    if selected_log:
                        log_path = os.path.join(user_dir, selected_log)

                        # Step 3: Read the selected .log file
                        with open(log_path, "r", encoding="utf-8") as f:
                            log_content = f.readlines()

                        # Step 4: Optional keyword and date filters
                        with st.expander("🔍 Filter Options"):
                            keyword = st.text_input("Filter by keyword (optional):", "")
                            date_filter = st.text_input("Filter by date (YYYY-MM-DD, optional):", "")

                        # Apply filters if provided
                        filtered_logs = log_content
                        if keyword:
                            filtered_logs = [line for line in filtered_logs if keyword.lower() in line.lower()]
                        if date_filter:
                            filtered_logs = [line for line in filtered_logs if date_filter in line]

                        # Step 5: Display filtered or full log content
                        st.subheader("🧾 Log Preview")
                        st.text("".join(filtered_logs) if filtered_logs else "No matching logs found.")

                        # Step 6: Allow user to download the log (filtered or full)
                        st.download_button(
                            label="📥 Download Log File",
                            data="".join(filtered_logs),
                            file_name=selected_log,
                            mime="text/plain"
                        )

    # ---------------------------- TAB 3: JSON VIEWER ----------------------------
    st.divider()

    with tab3:
        st.subheader("Show Json File")

        # Create a form to toggle JSON file visibility
        with st.form("show-json"):
            open_json = st.form_submit_button("Show / Hide Json File")

            # Initialize a toggle variable in Streamlit session state
            if "show_json" not in st.session_state:
                st.session_state.show_json = False

            # Toggle the visibility when button is clicked
            if open_json:
                st.session_state.show_json = not st.session_state.show_json

            # Display JSON content if toggle is enabled
            if st.session_state.show_json:
                try:
                    # Check if file exists
                    if not os.path.exists("data/msms.json"):
                        st.warning("⚠️ JSON file not found.")
                    else:
                        # Read and display JSON content
                        with open("data/msms.json", "r") as f:
                            data = json.load(f)
                        st.json(data, expanded=True)
                except json.JSONDecodeError:
                    st.warning("⚠️ JSON file is empty or invalid.")
