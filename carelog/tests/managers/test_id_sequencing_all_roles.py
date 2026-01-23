# indent=2
import re
import importlib

import app.schedule as sch
sch = importlib.reload(sch)

from app.user import User
from app.patient import PatientUser
from app.doctor import DoctorUser
from app.nurse import NurseUser
from app.receptionist import ReceptionistUser
from app.admin import AdminUser

def _num(s: str) -> int:
  m = re.search(r"(\d+)$", s)
  return int(m.group(1)) if m else -1

def test_role_id_sequencing_survives_save_reload(tmp_path):
  data_path = tmp_path / "msms.json"
  ScheduleManager = sch.ScheduleManager

  sc1 = ScheduleManager(str(data_path))
  # Baseline next ids for empty store
  assert User.get_next_id(sc1, "patient").startswith("P")
  assert User.get_next_id(sc1, "doctor").startswith("D")
  assert User.get_next_id(sc1, "nurse").startswith("N")
  assert User.get_next_id(sc1, "receptionist").startswith("R")
  assert User.get_next_id(sc1, "admin").startswith("A")

  # Seed one of each
  p = PatientUser("P0001", "puser", "Pw1!x", "Pat", "2000-01-01", "X", "addr", "p@x.com", "012", "2025-10-26", [], "")
  d = DoctorUser("D0001", "duser", "Pw1!y", "Doc", "1990-01-01", "Y", "addr", "d@x.com", "011", "2024-01-01", "Gen", "Ward")
  n = NurseUser("N0001", "nuser", "Pw1!z", "Nur", "1992-02-02", "Z", "addr", "n@x.com", "010", "2024-02-02", "Gen", "Ward", "D0001")
  r = ReceptionistUser("R0001", "ruser", "Pw1!r", "Rec", "1995-03-03", "F", "addr", "r@x.com", "009", "2024-03-03")
  a = AdminUser("A0001", "auser", "Pw1!a", "Adm", "1985-04-04", "M", "addr", "a@x.com", "008", "2023-01-01")
  sc1.add_user("patient", p)
  sc1.add_user("doctor", d)
  sc1.add_user("nurse", n)
  sc1.add_user("receptionist", r)
  sc1.add_user("admin", a)
  sc1.save()

  # Reload fresh manager
  sc2 = ScheduleManager(str(data_path))

  # Next IDs should have advanced beyond the seeded ones
  assert _num(User.get_next_id(sc2, "patient")) >= 2
  assert _num(User.get_next_id(sc2, "doctor")) >= 2
  assert _num(User.get_next_id(sc2, "nurse")) >= 2
  assert _num(User.get_next_id(sc2, "receptionist")) >= 2
  assert _num(User.get_next_id(sc2, "admin")) >= 2