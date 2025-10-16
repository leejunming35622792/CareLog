from app.patient import PatientUser
from datetime import date

def test_patient_user_init():
    user = PatientUser(
        "P0001", "john123", "Pass123",
        "John Doe", "Male", "123 Street",
        "john@example.com", "0123456789",
        date(2025, 10, 5),
        ["Checkup record"],
        "Healthy"
    )

    assert user.p_id == "P0001"
    assert user.username == "john123"
    assert user.password == "Pass123"
    assert user.name == "John Doe"
    assert user.gender == "Male"
    assert user.address == "123 Street"
    assert user.email == "john@example.com"
    assert user.contact_num == "0123456789"
    assert user.date_joined == date(2025, 10, 5)
    assert user.p_record == ["Checkup record"]
    assert user.p_remark == "Healthy"

def test_create_acc_defaults():
    from datetime import date
    joined_date = date(2025, 10, 5)

    user = PatientUser.create_acc("P0002", "newuser", "Pwd123", joined_date)

    assert isinstance(user, PatientUser)
    assert user.p_id == "P0002"
    assert user.username == "newuser"
    assert user.password == "Pwd123"
    assert user.date_joined == joined_date
    assert user.p_record == []   # default
    assert user.p_remark == ""   # default
