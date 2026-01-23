# tests/test_doctor_user.py
import pytest
from app.doctor import DoctorUser

# Working
def test_doctor_user_creation():
    doctor = DoctorUser(
        d_id=1,
        username="docuser",
        password="Password1A",
        name="Dr. Alice",
        bday="1980-05-10",
        gender="Female",
        address="123 Clinic St",
        email="alice@hospital.com",
        contact_num="0123456789",
        date_joined="2025-01-01",
        speciality="Cardiology",
        department="Heart"
    )

    assert doctor.d_id == 1
    assert doctor.username == "docuser"
    assert doctor.name == "Dr. Alice"
    assert doctor.speciality == "Cardiology"
    assert doctor.department == "Heart"
    assert doctor.__str__() == "Doctor Dr. Alice (Cardiology, Heart)"
