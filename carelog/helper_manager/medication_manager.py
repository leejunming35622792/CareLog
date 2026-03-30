import datetime

from app.schedule import ScheduleManager
from app.patient import PatientRecord

manager = ScheduleManager()

# Saves data using the manager's save method, handling both save data and save attributes
def _persist():
	try:
		if hasattr(manager, "_save_data"):
			manager._save_data()
		elif hasattr(manager, "save"):
			manager.save()
	except Exception:
		pass

# Converts input to a list of non-empty strings, handling None, lists, or comma-seperated strings
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

# Generates the next patient record ID in the format PRxxxx based on existing records
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

# Retrieves the latest patient record for a given patient ID, sorted by timestamp
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

# Replaces medications in a specific patient record
def edit_medications(record_id, medications):
	rec = next((r for r in manager.records if getattr(r, "pr_record_id", None) == record_id), None)
	if rec is None:
		return False, "Record not found"
	rec.pr_medications = _to_list(medications)
	_persist()
	return True, "Replaced Medication"

# Removes a specific medication from a patient record
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

# Retrieves medications for a patient, either per record or as a unique list
def list_medications(patient_id, per_record=False):
	pid = str(patient_id)
	patient = next((p for p in manager.patients if str(p.p_id) == pid), None)
	if patient is None:
		return False, "Patient Not Found", []
	# retrieve medications
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
	#retrieve unique medications
	all_meds = []
	for r in manager.records:
		if str(getattr(r, "p_id", "")) == pid:
			for m in _to_list(getattr(r, "pr_medications", None)):
				if m not in all_meds:
					all_meds.append(m)
	return True, f"Found {len(all_meds)} unique medication(s)", all_meds
