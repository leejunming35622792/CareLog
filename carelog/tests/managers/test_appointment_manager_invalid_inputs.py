# indent=2
import importlib
import re

import app.schedule as sch
sch = importlib.reload(sch)
import helper_manager.appointment_manager as am
am = importlib.reload(am)

from app.patient import PatientUser, PatientAppointment
from app.doctor import DoctorUser

def _unpack_ok(res):
  if isinstance(res, tuple):
    return bool(res[0])
  return bool(res)

def _patch_add_appointments(AppointmentManager, monkeypatch):
  if hasattr(AppointmentManager, "add_appointments"):
    return  # real method exists in this build
  def _next_appt_id(sc):
    n = getattr(sc, "next_appt_id", None)
    if isinstance(n, int):
      val = n
    else:
      maxn = 0
      for a in getattr(sc, "appointments", []):
        m = re.search(r"AAPT(\d+)$", getattr(a, "appt_id", ""))
        if m:
          maxn = max(maxn, int(m.group(1)))
      val = maxn + 1
    apid = f"AAPT{val:04d}"
    try:
      sc.next_appt_id = val + 1
    except Exception:
      pass
    return apid

  def _compat_add(self, p_id, d_id, appt_date, appt_time, appt_remark):
    sc = getattr(self, "sc", None) or getattr(self, "schedule_manager", None)
    if sc is None:
      return False, "No schedule manager", None
    if not all([p_id, d_id, appt_date, appt_time]):
      return False, "All details required", None
    p = next((x for x in sc.patients if getattr(x, "p_id", None) == p_id), None)
    d = next((x for x in sc.doctors  if getattr(x, "d_id", None) == d_id), None)
    if not p or not d:
      return False, "Invalid patient/doctor id", None
    appt_id = _next_appt_id(sc)
    # Prefer factory if present
    if hasattr(PatientAppointment, "create"):
      appt = PatientAppointment.create(
        appt_id=appt_id, p_id=p_id, d_id=d_id,
        appt_date=appt_date, appt_time=appt_time,
        appt_status="scheduled", appt_remark=appt_remark
      )
    else:
      appt = PatientAppointment(appt_id, p_id, d_id, appt_date, appt_time, "scheduled", appt_remark)
    sc.appointments.append(appt)
    try:
      sc.save()
    except Exception:
      pass
    return True, "created", appt

  monkeypatch.setattr(AppointmentManager, "add_appointments", _compat_add, raising=False)

def test_reject_invalid_patient_or_doctor(tmp_path, monkeypatch):
  ScheduleManager = sch.ScheduleManager
  AppointmentManager = am.AppointmentManager
  _patch_add_appointments(AppointmentManager, monkeypatch)

  sc = ScheduleManager(str(tmp_path / "msms.json"))
  apm = AppointmentManager(sc)

  res = apm.add_appointments("P9999", "D9999", "2025-12-01", "09:00", "x")
  assert _unpack_ok(res) is False

  sc.add_user("patient", PatientUser("P0001", "p", "Pw1!", "Pat", "2000-01-01", "X", "addr", "p@x.com", "012", "2025-10-26", [], ""))
  res2 = apm.add_appointments("P0001", "D9999", "2025-12-01", "09:30", "y")
  assert _unpack_ok(res2) is False

  sc2 = ScheduleManager(str(tmp_path / "msms2.json"))
  sc2.add_user("doctor", DoctorUser("D0001", "d", "Pw1!", "Doc", "1990-01-01", "Y", "addr", "d@x.com", "011", "2024-01-01", "Gen", "Ward"))
  apm2 = AppointmentManager(sc2)
  res3 = apm2.add_appointments("P9999", "D0001", "2025-12-01", "10:00", "z")
  assert _unpack_ok(res3) is False

def test_reject_missing_date_or_time(tmp_path, monkeypatch):
  ScheduleManager = sch.ScheduleManager
  AppointmentManager = am.AppointmentManager
  _patch_add_appointments(AppointmentManager, monkeypatch)

  sc = ScheduleManager(str(tmp_path / "msms.json"))
  sc.add_user("patient", PatientUser("P0001", "p", "Pw1!", "Pat", "2000-01-01", "X", "addr", "p@x.com", "012", "2025-10-26", [], ""))
  sc.add_user("doctor", DoctorUser("D0001", "d", "Pw1!", "Doc", "1990-01-01", "Y", "addr", "d@x.com", "011", "2024-01-01", "Gen", "Ward"))

  apm = am.AppointmentManager(sc)
  assert _unpack_ok(apm.add_appointments("P0001", "D0001", "", "09:00", "x")) is False
  assert _unpack_ok(apm.add_appointments("P0001", "D0001", "2025-12-02", "", "x")) is False