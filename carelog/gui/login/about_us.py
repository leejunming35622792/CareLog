import streamlit as st

def about_us(manager):
    st.image("img\\wallpaper.jpg")

    st.markdown(
    """
    ### 🏥 Welcome to :rainbow[CareLog]

    At **CareLog**, we believe that every hospital should be more than a place of treatment — it should be a place of **compassion, dignity, and respect**.  

    Our focus is on creating an environment where:

    - Patients feel :red[**heard**], :red[**cared**] for, and :red[**supported**] 
    - Staff are empowered to provide not just clinical care, but also **empathetic, human-centred support**

    **Your health, your comfort, your dignity — always our priority.**
    """,
    unsafe_allow_html=True
    )

    st.divider()