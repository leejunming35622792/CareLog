# indent=2
import re
from pathlib import Path

from app.schedule import ScheduleManager
from app.patient import PatientUser
from app.doctor import DoctorUser
from app.user import User

def _num(s: str) -> int:
  return int(re.findall(r"(\d+)$", s)[0])

def test_save_reload_preserves_users_and_ids(tmp_path):
  data_path = tmp_path / "msms.json"

  # Fresh manager (no fixture -> no monkeypatch)
  sc1 = ScheduleManager(str(data_path))
  assert isinstance(sc1.patients, list)
  assert isinstance(sc1.doctors, list)

  # Seed one patient and one doctor
  p1_id = "P0001"
  d1_id = "D0001"
  p1 = PatientUser(
    p_id=p1_id,
    username="alice",
    password="Pw1!Alice",
    name="Alice Patient",
    bday="1995-01-01",
    gender="Female",
    address="1 Health St",
    email="alice@example.com",
    contact_num="0123456789",
    date_joined="2025-10-26",
    p_record=[],
    p_remark=""
  )
  d1 = DoctorUser(
    d_id=d1_id,
    username="drbob",
    password="Pw1!Bob",
    name="Bob Doctor",
    bday="1980-06-06",
    gender="Male",
    address="2 Clinic Rd",
    email="bob@example.com",
    contact_num="0111111111",
    date_joined="2024-01-01",
    speciality="General",
    department="Ward A"
  )
  sc1.add_user("patient", p1)
  sc1.add_user("doctor", d1)
  sc1.save()

  # Reload a brand-new manager from disk
  sc2 = ScheduleManager(str(data_path))

  # Users persisted
  assert any(p.p_id == p1_id and p.username == "alice" for p in sc2.patients)
  assert any(d.d_id == d1_id and d.username == "drbob" for d in sc2.doctors)

  # ID sequencing (tolerant): next patient id should advance beyond P0001
  next_pid = User.get_next_id(sc2, "patient")
  assert next_pid.startswith("P")
  assert _num(next_pid) >= 2