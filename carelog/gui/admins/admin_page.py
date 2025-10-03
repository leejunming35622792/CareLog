import streamlit as st

def dashboard():
    st.write("This is the Dashboard")

def admin_page(Manager):
    # Variables
    global manager
    manager = Manager
    global username
    username = st.session_state.username
    tabs = ["Dashboard", "Profile", "Management", "Records"]

    # Session state
    if "logout_triggered" in st.session_state and st.session_state.logout_triggered:
        st.session_state.logout_triggered = False
        st.rerun()

    # Page design
    st.title(f"CareLog Dashboard - Welcome {username}")
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select", tabs)
    st.sidebar.button("Logout", on_click=logout)
    st.subheader("TBC")

    if option == "Dashboard":
        dashboard()
    elif option == "Profile":
        st.write("This is the Profile Page")
    elif option == "Management":
        tab1, tab2 = st.tabs(["User Management", "Appointment"])

        with tab1:
            st.subheader("User Management")

            user_type = st.selectbox("User type", ["Patient", "Doctor", "Nurse", "Receptionist"])
            match user_type:
                case "Patient":
                    name = st.text_input("Name", key="register_name")
                    password = st.text_input("Password", type="password", key="register_password")
                    username = st.text_input("Username", key="register_username")
                    gender = st.selectbox("Gender", ["Male, Female, Other"], key="register_gender")
                    address = st.text_input("Address", key="register_address")
                    email = st.text_input("Email", key="register_email")
                    contact = st.text_input("Contact", key="register_contact")

                case "Doctor":
                    name = st.text_input("Name", key="register_name")
                    password = st.text_input("Password", type="password", key="register_password")
                    username = st.text_input("Username", key="register_username")
                    gender = st.selectbox("Gender", ["Male, Female, Other"], key="register_gender")
                    address = st.text_input("Address", key="register_address")
                    email = st.text_input("Email", key="register_email")
                    contact = st.text_input("Contact", key="register_contact")
                case "Nurse":
                    name = st.text_input("Name", key="register_name")
                    password = st.text_input("Password", type="password", key="register_password")
                    username = st.text_input("Username", key="register_username")
                    gender = st.selectbox("Gender", ["Male, Female, Other"], key="register_gender")
                    address = st.text_input("Address", key="register_address")
                    email = st.text_input("Email", key="register_email")
                    contact = st.text_input("Contact", key="register_contact")
                case "Receptionist":
                    name = st.text_input("Name", key="register_name")
                    password = st.text_input("Password", type="password", key="register_password")
                    username = st.text_input("Username", key="register_username")
                    gender = st.selectbox("Gender", ["Male, Female, Other"], key="register_gender")
                    address = st.text_input("Address", key="register_address")
                    email = st.text_input("Email", key="register_email")
                    contact = st.text_input("Contact", key="register_contact")

            # Create a register button
            if st.button("Register", key="register_button"):
                if user_type == "Patient":
                    success, message, _ = Manager.register_new_patient(name, password, username, gender, address, email, contact)
                elif user_type == "Doctor":
                    success, message, _ = Manager.register_new_doctor(name, password, username, gender, address, email, contact)
                elif user_type == "Nurse":
                    success, message, _ = Manager.register_new_doctor(name, password, username, gender, address, email, contact)
                elif user_type == "Receptionist":
                    success, message, _ = Manager.register_new_receptionist(name, password, username, gender, address, email, contact)
                if success:
                    st.success(message)
                    st.info("Account created")
                else:
                    st.error(message)


        st.write("This is the Appointments Page")
        st.write("This is the Management Page")

    elif option == "3":
        st.write("This is the Records Page")

def register(prompt):
    pass

def logout():
    st.session_state.page = "login"
    st.session_state.username = None
    st.session_state.logout_triggered = True