import datetime

from app.schedule import ScheduleManager
from app.patient import PatientRecord

manager = ScheduleManager()

def _persist():
	try:
		if hasattr(manager, "_save_data"):
			manager._save_data()
		elif hasattr(manager, "save"):
			manager.save()
	except Exception:
		pass


def _to_list(value):
	if value is None:
		return []
	if isinstance(value, list):
		return [str(x).strip() for x in value if str(x).strip()]
	s = str(value).strip()
	if not s:
		return []
	if "," in s:
		return [p.strip() for p in s.split(",") if p.strip()]
	return [s]


def _next_pr_id():
	max_n = 0
	for r in getattr(manager, "records", []):
		rid = getattr(r, "pr_record_id", "")
		if isinstance(rid, str) and rid.startswith("PR"):
			try:
				n = int(rid[2:])
				if n > max_n:
					max_n = n
			except Exception:
				continue
	return f"PR{max_n + 1:04d}"


def _latest_record(patient_id):
	pid = str(patient_id)
	records = [r for r in getattr(manager, "records", []) if str(getattr(r, "p_id", "")) == pid]
	if not records:
		return None
	def _parse(ts):
		try:
			return datetime.datetime.fromisoformat(ts)
		except Exception:
			return ts
	return sorted(records, key=lambda r: _parse(getattr(r, "pr_timestamp", "")), reverse=True)[0]


def assign_medications(patient_id, doctor_id, conditions, medications, doctor_username, pr_prediction_result, pr_confidence_score, instructions="", new_record=False):
	meds = _to_list(medications)
	if not meds:
		return False, "No medications provided", None

	patient = next((p for p in manager.patients if str(p.p_id) == str(patient_id)), None)
	if patient is None:
		return False, "Patient Not Found", None

	if new_record:
		if not doctor_username:
			return False, "doctor_username is required to create a new record", None
		doctor = next((d for d in manager.doctors if d.username == doctor_username), None)
		if doctor is None:
			return False, "Doctor Not Found", None

		pr_id = _next_pr_id()
		ts = datetime.datetime.utcnow().isoformat(timespec="seconds")
		remark = f"Prescribed by {getattr(doctor, 'name', doctor_username)} ({doctor_username})"
		if instructions:
			remark += f". Note: {instructions}"

		rec = PatientRecord(
			pr_record_id=pr_id,
			p_id=patient.p_id,
			d_id=doctor_id,
			pr_timestamp=ts,
			pr_conditions=conditions,
			pr_medications=meds,
			pr_billings=0.0,
			pr_prediction_result=pr_prediction_result,
			pr_confidence_score=pr_confidence_score,
			pr_remark=remark,
		)
		manager.records.append(rec)
		_persist()
		return True, "Prescription recorded", pr_id

	
	latest = _latest_record(patient_id)
	if latest is None:
		if doctor_username:
			return assign_medications(patient_id, meds, doctor_username, instructions, new_record=True)
		return False, "No existing record; provide doctor_username or set new_record=True", None

	current = _to_list(getattr(latest, "pr_medications", None))
	for m in meds:
		if m not in current:
			current.append(m)
	latest.pr_medications = current
	_persist()
	return True, "Medications updated", latest.pr_record_id


def edit_medications(record_id, medications):
	rec = next((r for r in manager.records if getattr(r, "pr_record_id", None) == record_id), None)
	if rec is None:
		return False, "Record not found"
	rec.pr_medications = _to_list(medications)
	_persist()
	return True, "Replaced Medication"


def remove_medication(record_id, medication):
	rec = next((r for r in manager.records if getattr(r, "pr_record_id", None) == record_id), None)
	if rec is None:
		return False, "Record is not found"
	current = _to_list(getattr(rec, "pr_medications", None))
	target = str(medication).strip()
	new_list = [m for m in current if m != target]
	rec.pr_medications = new_list
	_persist()
	return True, ("Medication removed" if len(new_list) != len(current) else "Medication not found")


def list_medications(patient_id, per_record=False):
	pid = str(patient_id)
	patient = next((p for p in manager.patients if str(p.p_id) == pid), None)
	if patient is None:
		return False, "Patient Not Found", []

	if per_record:
		rows = []
		for r in manager.records:
			if str(getattr(r, "p_id", "")) == pid:
				rows.append({
					"record_id": getattr(r, "pr_record_id", ""),
					"timestamp": getattr(r, "pr_timestamp", ""),
					"medications": _to_list(getattr(r, "pr_medications", None)),
				})
		return True, f"Found {len(rows)} record(s)", rows
	all_meds = []
	for r in manager.records:
		if str(getattr(r, "p_id", "")) == pid:
			for m in _to_list(getattr(r, "pr_medications", None)):
				if m not in all_meds:
					all_meds.append(m)
	return True, f"Found {len(all_meds)} unique medication(s)", all_meds