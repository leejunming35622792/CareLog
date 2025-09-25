import streamlit as st

def register():
    st.title("Register Account")
    
    st.balloons()

    st.info("Welcome! To register a new account, please choose an username and password")

    with st.form("register-form"):
        username = st.text_input("Enter New Username: ")
        password = st.text_input("Enter New Password: ")

        