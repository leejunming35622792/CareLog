def test_create_appointment_success(tmp_manager):
    rcp = next(r for r in tmp_manager.receptionists if r.username == "rcp1")
    ok, msg, appt = rcp.create_appointment(
        tmp_manager, "P0001", "D0001",
        appt_date="2025-11-01", appt_time="10:00", remark="First visit"
    )
    assert ok is True
    assert appt is not None
    assert any(a.appt_id == appt.appt_id for a in tmp_manager.appointments)

def test_create_appointment_invalid_ids(tmp_manager):
    rcp = next(r for r in tmp_manager.receptionists if r.username == "rcp1")
    ok, msg, appt = rcp.create_appointment(
        tmp_manager, "P9999", "D9999", appt_date="2025-11-01", appt_time="14:00"
    )
    assert ok is False
    assert appt is None