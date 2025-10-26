import datetime

def test_register_user_success(tmp_manager, monkeypatch):
  # Shim to match how admin.register_user calls User.create_user in your build
  from app import user as user_module
  from app.patient import PatientUser

  def _fake_create_user(sc, role, next_id, username, password, name, bday, gender, address, email, contact, date_joined):
    if role == "patient":
      new_user = PatientUser(
        p_id=next_id,
        username=username,
        password=password,
        name=name,
        bday=str(bday),
        gender=gender,
        address=address,
        email=email,
        contact_num=contact,
        date_joined=str(date_joined),
        p_record=[],
        p_remark=""
      )
      sc.patients.append(new_user)
      sc.save()
      return True, "created", new_user
    # Fallback: behave like a failure for roles we didn't stub
    return False, "not implemented in test shim", None

  monkeypatch.setattr(user_module.User, "create_user", staticmethod(_fake_create_user))

  admin = next(a for a in tmp_manager.admins if a.username == "admin1")
  ok, msg, user = admin.register_user(
    role="patient",
    username="newpatient",
    password="ValidPass1",
    name="New Patient",
    bday=datetime.date(2001, 1, 2),
    gender="Male",
    address="6 Street",
    email="newpatient@example.com",
    contact="0999999999"
  )
  assert ok is True
  assert user is not None
  assert any(p.username == "newpatient" for p in tmp_manager.patients)


def test_register_user_missing_fields(tmp_manager):
  admin = next(a for a in tmp_manager.admins if a.username == "admin1")
  ok, msg, user = admin.register_user(
    role="patient",
    username="",
    password="",
    name="X",
    bday=datetime.date(2001, 1, 1),
    gender="Male",
    address="Addr",
    email="bad@example.com",
    contact="012"
  )
  assert ok is False
  assert user is None