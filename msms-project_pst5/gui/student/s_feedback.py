import streamlit as st

# --- Sub-section: Feedback ---
def feedback():
    # Variable
    manager = st.session_state.manager
    username = st.session_state.username
    password = st.session_state.password
    current_student = next((s for s in manager.students if s.username == username), None)
    current_course = current_student.enrolled_course_ids
    
    with st.form("feedback-form"):
        course_disp = {f"{c.id} - {c.name}": c.id for c in manager.courses if current_student.id in c.enrolled_student_ids}

        if course_disp:
            choose_course = st.selectbox("Select Course", course_disp.keys())
        else:
            st.warning("⚠️ Database is empty, no courses found")
        
        like = st.feedback()

        comment = st.text_area("Anything You Wish to Say:")

        submit = st.form_submit_button("Submit Feedback")
        
        if submit:
            new_feedback = {choose_course: f"{like}, {comment}"}
            manager.save_feedback(new_feedback)
            
            st.success("Thanks for your valuable feedback! 😊")


