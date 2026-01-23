def test_remove_user_success(tmp_manager):
    admin = next(a for a in tmp_manager.admins if a.username == "admin1")
    ok, msg = admin.remove_user("patient", "P0001")
    assert ok is True
    assert all(p.p_id != "P0001" for p in tmp_manager.patients)

def test_remove_user_not_found(tmp_manager):
    admin = next(a for a in tmp_manager.admins if a.username == "admin1")
    ok, msg = admin.remove_user("patient", "P9999")
    assert ok is False