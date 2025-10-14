import streamlit as st
import pandas as pd
import base64
import json
from PIL import Image
import io
import time
import logging

def payment(manager):
    st.title("Payment & Finance")
    tab1, tab2 = st.tabs(["Make Payment", "View Payments"])

    with tab1:
        make_payment()
    with tab2:
        view_payment()

def make_payment():
    # Variables
    manager = st.session_state.manager
    username = st.session_state.username
    all_student = {f"{s.id} - {s.name}":s.id for s in manager.students}

    with st.form("pay_form"):
        st.header("Finance & Payment")
        student = st.selectbox("Select Student:", all_student.keys())
        amount = st.text_input("Enter Amount:")
        method = st.selectbox("Select Payment Method", ["Cash", "Bank Transfer", "E-Wallet"])
        upload_file = st.file_uploader("Upload Receipt", type=["jpg", "jpeg", "png"])

        if upload_file:
            image = Image.open(upload_file)
            st.image(image, caption="Uploaded Image Preview")

        pay_button = st.form_submit_button("Continue")

        if pay_button:
            errors = []

            # Input validations
            if not amount:
                errors.append("Please enter amount!")
            if not method:
                errors.append("Please select payment method!")
            if upload_file is None:
                errors.append("Please upload the payment receipt!")
            if not student:
                errors.append("Please select a student!")
            else:
                current_student = student[all_student]

            # Stop if errors exist
            if errors:
                for e in errors:
                    st.error(e)
                st.stop()

            # Proceed with payment
            result = manager.add_payment(username, amount, method, upload_file)

            if result:
                with st.spinner("Submitting..."):
                    time.sleep(1.5)
                    manager.save()
                logging.info(f"Make Payment of RM{amount}")
                st.success(f"Payment of RM{amount} for student {current_student} recorded successfully!")
            else:
                st.error("Payment failed. Please try again.")

def view_payment():
    import datetime
    import streamlit as st

    manager = st.session_state.manager
    username = st.session_state.username
    current_student = next((s for s in manager.students if s.username == username), None)

    all_student = {f"{s.id} - {s.name}":s.id for s in manager.students}

    if not all_student:
        st.warning("No students found!")
        st.stop()
    else:
        student_disp = st.selectbox("Select Student:", all_student.keys())
        student_id = all_student[student_disp]

    # Filter payments for this student
    student_payments = manager.get_payment_history(student_id)

    if not student_payments:
        st.warning("No payment records found for your account!")
        st.stop()

    indexed_dates = {i: date for i, date in enumerate(student_payments)}

    if len(student_payments) == 1:
        selected_payment = student_payments[0]
    else:
        # 🎚 Slider uses numeric indices, but label shows the date
        selected_index = st.slider(
            "Slide through payment dates",
            min_value=0,
            max_value=len(student_payments)-1,
            format="%d"
        )

        selected_payment = indexed_dates[selected_index]

    # Convert payment from object to dictionary
    payment_dict = manager.payment_to_dict(selected_payment)

    # Display in Dataframe
    payment_df = pd.DataFrame(payment_dict.items(), columns=["Field", "Value"])
    st.dataframe(payment_df, hide_index=True)

    # Display receipt
    show_image = st.button("Show Receipt")
    if show_image:
        st.image(selected_payment.receipt)
