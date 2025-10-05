import streamlit as st

def dashboard(manager, username):
    # Page design
    st.title("Welcome to CareLog!")
    st.balloons()

    st.image("img/dashboard.png")

    st.text("🏥 At CareLog, we believe that every hospital should be more than a place of treatment — it should be a place of compassion, dignity, and respect. Our focus is on creating an environment where patients feel heard, cared for, and supported, while staff are empowered to provide not just clinical care, but also empathetic, human-centred support.")

    st.divider()

    m1, m2, m3 = st.columns(3)

    with m1:
        d_count = manager.get_doctor_count()
        st.metric("Total Medical Staff", d_count)
    with m2:
        p_count = manager.get_patient_count()
        st.metric("Total Patient", p_count) 
