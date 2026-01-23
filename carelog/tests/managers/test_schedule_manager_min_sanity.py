# indent=2
from app.schedule import ScheduleManager

def test_new_manager_starts_clean(tmp_path):
  sc = ScheduleManager(str(tmp_path / "msms.json"))
  # Minimal invariants
  assert isinstance(sc.patients, list)
  assert isinstance(sc.doctors, list)
  assert isinstance(sc.nurses, list)
  assert isinstance(sc.receptionists, list)
  assert isinstance(sc.admins, list)
  assert isinstance(sc.records, list)
  assert isinstance(sc.appointments, list)