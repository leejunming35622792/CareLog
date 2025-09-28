import streamlit as st
import pandas as pd

def show_print_student_card_page(manager):
    st.header("Print Student Card")
    with st.form("print_form"):
        id_disp = {f"{s.id} - {s.name}": s.id for s in manager.students}
        id_list = st.selectbox("Select Student ID:",id_disp.keys())

        # Create buttons
        view_button = st.form_submit_button("View Student Info")
        print_button = st.form_submit_button("Print Student Card")

        # To view student info
        if view_button:
            if id_list:
                s_id = id_disp[id_list]
                
                student_info = next((s for s in manager.students if str(s.id) == str(s_id)), None)
                course_info = [c for c in manager.courses if student_info.id in c.enrolled_student_ids]
                match_teacher = {t.id: t.name for t in manager.teachers}

                card = (
                    "Student Card:\n\n"
                    + "+" + "="*50 + "+\n"
                    + "|{:^50}|\n".format("MUSIC SCHOOL ID BADGE")
                    + "+" + "="*50 + "+\n"
                    + "| {:20} {:<28}|\n".format("ID", student_info.id)
                    + "| {:20} {:<28}|\n".format("Name", student_info.name)
                    + "+" + "="*50 + "+\n"
                )

                # Add course details dynamically
                for c in course_info:
                    card += "| {:20} {:<28}|\n".format(f"Course {c.id}", c.name)
                    card += "|      {:15} {:<28}|\n".format(f"Teacher: ", match_teacher[c.teacher_id])
                    card += "|      {:15} {:<28}|\n".format(f"Instrument: ", c.instrument)
                    card += "|" + " "*50 + "|\n"

                # Finish the card
                card += "+" + "="*50 + "+\n"
                card += "|{:^50}|\n".format("CONGRATULATIONS!")
                card += "+" + "="*50 + "+\n"

                st.code(card)

            else:
                st.warning("⚠️ No Students!")

        # To print student info
        if print_button:
            if id_list:
                s_id = id_disp[id_list]
                result = manager.print_card(s_id)
                if result:
                    st.success(f"Printed student card to {result}.")
                else:
                    st.warning(f"ID '{s_id}' is not found!")
            else:
                st.warning("⚠️ No Students!")