import streamlit as st

# --- Sub-section: Feedback ---
def student_card():
    # Variable
    manager = st.session_state.manager
    username = st.session_state.username
    password = st.session_state.password
    current_student = next((s for s in manager.students if s.username == username), None)
    current_course = current_student.enrolled_course_ids

    st.subheader("Your Student Card: ")
    current_student = next((s for s in manager.students if s.username == username), None)
    course_info = [c for c in manager.courses if current_student.id in c.enrolled_student_ids]
    match_teacher = {t.id: t.name for t in manager.teachers}

    card = (
        "+" + "=" * 70 + "+\n"
        + "|{:^70}|\n".format("MUSIC SCHOOL ID BADGE")
        + "+" + "=" * 70 + "+\n"
        + "|  {:24} {:<43}|\n".format("ID", current_student.id)
        + "|  {:24} {:<43}|\n".format("Name", current_student.name)
        + "+" + "=" * 70 + "+\n"
    )

    # Add course details dynamically
    for c in course_info:
        card += "| {:.<25} {:<43}|\n".format(f"Course {c.id}", c.name)
        card += "|            {:.<15}{:<42} |\n".format(f"Teacher", match_teacher[c.teacher_id])
        card += "|         {:.<18}{:<42} |\n".format(f"Instrument", c.instrument)
        card += "|" + " " * 70 + "|\n"

    # Finish the card
    card += "+" + "=" * 70 + "+\n"
    card += "|{:^70}|\n".format("CONGRATULATIONS!")
    card += "+" + "=" * 70 + "+\n"

    st.code(card)