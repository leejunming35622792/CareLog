from app.patient import PatientUser
from datetime import date

# --- Test creating new patient ---
def test_patient_user_init():
    user = PatientUser(
        p_id="P0001", 
        username="john123", 
        password="Pass123",
        name="John Doe", 
        gender="Male", 
        address="123 Street",
        email="john@example.com", 
        contact_num="0123456789",
        date_joined=(2025, 10, 5),
        p_record=[{
            "pr_record_id": "PR0002",
            "p_id": "P0001",
            "d_id": "D0001",
            "pr_timestamp": "2025-04-12T10:00:00",
            "pr_conditions": "Fractured arm",
            "pr_medications": "Painkillers",
            "pr_billings": 250.0,
            "pr_prediction_result": "Moderate risk",
            "pr_confidence_score": 0.85,
            "pr_remark": "Bone checkup"
        }],
        p_remark="Healthy"
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
    assert user.p_record == [{
        "pr_record_id": "PR0002",
        "p_id": "P0001",
        "d_id": "D0001",
        "pr_timestamp": "2025-04-12T10:00:00",
        "pr_conditions": "Fractured arm",
        "pr_medications": "Painkillers",
        "pr_billings": 250.0,
        "pr_prediction_result": "Moderate risk",
        "pr_confidence_score": 0.85,
        "pr_remark": "Bone checkup"
    }]
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
