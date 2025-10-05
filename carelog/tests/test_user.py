# tests/test_user.py
from app.user import User

# --- MOCK manager class for testing ---
class MockUser:
    def __init__(self):
        class Patient:
            def __init__(self, username):
                self.username = username
                self.password = "OldPass1"
                self.name = "John"
                self.gender = "Male"
                self.address = "Old Street"
                self.email = "john@old.com"
                self.contact_num = "0123456789"
                self.p_remark = "Old remark"

        self.patients = [Patient("john123")]
        self.saved = False

    def _save_data(self):
        self.saved = True


# ---------- TESTS START HERE ----------
def test_update_patient_detail_success():
    """Positive test — should update patient details successfully"""
    manager = MockUser()
    result = User.update_patient_detail(
        manager,
        username="john123",
        new_password="NewPass1",
        new_name="John Doe",
        new_gender="Male",
        new_address="New Street",
        new_email="john@new.com",
        new_contact_num="0198765432",
        new_remark="Updated"
    )

    assert result is True
    assert manager.patients[0].password == "NewPass1"
    assert manager.patients[0].name == "John Doe"
    assert manager.saved is True


def test_update_patient_detail_invalid_username():
    """Negative test — username not found"""
    manager = MockUser()
    result = User.update_patient_detail(
        manager,
        username="wrong_user",
        new_password="Pass123",
        new_name="Someone",
        new_gender="Male",
        new_address="Address",
        new_email="email@test.com",
        new_contact_num="0123456789",
        new_remark="Remark"
    )
    assert result is False


def test_get_next_id_valid_roles(monkeypatch):
    """Positive test — get_next_id should return correct format"""
    class MockSchedule:
        next_patient_id = 1
        next_doctor_id = 2
        next_nurse_id = 3
        next_receptionist_id = 4
        next_admin_id = 5

    monkeypatch.setattr("app.user.ScheduleManager", lambda: MockSchedule())

    assert User.get_next_id("patient") == "P0001"
    assert User.get_next_id("doctor") == "D0002"
    assert User.get_next_id("nurse") == "N0003"
    assert User.get_next_id("receptionist") == "R0004"
    assert User.get_next_id("admin") == "A0005"


def test_get_next_id_invalid_role():
    """Negative test — invalid role should raise ValueError"""
    with pytest.raises(ValueError):
        User.get_next_id("invalidrole")
