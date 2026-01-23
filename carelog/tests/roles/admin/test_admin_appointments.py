def test_admin_get_appointment_list_empty(tmp_manager):
    admin = next(a for a in tmp_manager.admins if a.username == "admin1")
    ok, msg, appts = admin.get_appointment("admin1", tmp_manager)
    assert isinstance(appts, list)

def test_admin_upcoming_appointment(tmp_manager):
    admin = next(a for a in tmp_manager.admins if a.username == "admin1")
    ok, msg, appts = admin.upcoming_appointment("admin1", tmp_manager)
    assert isinstance(appts, list)