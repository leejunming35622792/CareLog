import streamlit as st

def log_in(manager):
    # Variable
    user = ["Patient", "Doctor", "Nurse", "Receptionist"]

    # Page design
    st.title("CareLog")

    col1, col2 = st.columns(2)

    with col1:
        st.image("C:\\Users\\Owner\\FIT1056-Sem2-2025\\carelog\\img\\wallpaper.jpg")

    with col2:
        with st.form("register-form"):
            st.subheader("Login")
            staff = st.selectbox("User", user)
            username = st.text_input("Username: ")
            password = st.text_input("Password: ")
            button = st.form_submit_button("Login")

            if button:
                # Variables
                errors = []
                patient_acc = {p.username: p.password for p in manager.patients}
                doctor_acc = {d.username: d.password for d in manager.doctors}
                nurse_acc = {n.username: n.password for n in manager.nurses}
                receptionist_acc = {r.username: r.password for r in manager.receptionists}
                admin_acc = {a.username: a.password for a in manager.admins}

                if not username:
                    errors.append("Username cannot be empty!")
                if not password:
                    errors.append("Password cannot be empty!")
                
                if errors:
                    for e in errors:
                        st.error(e)
                    st.stop()

                if username in list(patient_acc.keys()):
                    if password == patient_acc.get(username):
                        st.session_state.page = "patient"
                        st.session_state.username = username
                elif username in list(doctor_acc.keys()):
                    if password == doctor_acc.get(username):
                        st.session_state.page = "doctor"
                        st.session_state.username = username
                elif username in list(nurse_acc.keys()):
                    if password == nurse_acc.get(username):
                        st.session_state.page = "nurse"
                        st.session_state.username = username
                elif username in list(receptionist_acc.keys()):
                    if password == receptionist_acc.get(username):
                        st.session_state.page = "receptionist"
                        st.session_state.username = username
                elif username in list(admin_acc.keys()):
                    if password == admin_acc.get(username):
                        st.session_state.page = "admin"
                        st.session_state.username = username
                else:
                    st.error("Username and password do not match!")

                    
                
