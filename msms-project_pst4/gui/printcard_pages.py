import streamlit as st
import pandas as pd

def show_print_student_card_page(manager):
    st.header("Print Student Card")
    with st.form("print_form"):
        # Create input box
        s_id = st.text_input("Enter Student ID: ")

        # Create buttons
        view_button = st.form_submit_button("View Student Info")
        print_button = st.form_submit_button("Print Student Card")

        # To view student info
        if view_button:
            student_info = manager.search_student(s_id)

            if student_info:
                student_df = pd.DataFrame(student_info)
                st.dataframe(student_df, hide_index=True)
            else:
                st.warning(f"ID '{s_id}' is not found!")

        # To print student info
        if print_button:
            result = manager.print_card(s_id)
            if result:
                st.success(f"Printed student card to {result}.")
            else:
                st.warning(f"ID '{s_id}' is not found!")