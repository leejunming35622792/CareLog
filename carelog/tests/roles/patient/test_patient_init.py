from app.patient import PatientUser

# Working
def test_patient_init_and_fields():
    p = PatientUser(
        p_id="P7777",
        username="pat777",
        password="Passw0rd!",
        name="Seven",
        bday="1999-09-09",
        gender="X",
        address="Somewhere",
        email="s@example.com",
        contact_num="0123",
        date_joined="2024-09-09",
        p_record=[],
        p_remark=""
    )
    assert p.p_id == "P7777"
    assert p.username == "pat777"