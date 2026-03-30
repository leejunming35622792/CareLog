# **CareLog — Streamlit-Based Healthcare Management System**

An integrated digital healthcare management platform for hospitals and clinics, built using Python and Streamlit. Designed to simplify and centralize operations for patients, doctors, nurses, admins and receptionist through a secure and role based access of features

---

## **Overview**
The CareLog application is a Streamlit-based workflow system for clinics that converts manual operations and tasks to be performed within a single digital application. The clinic operations are divided within across 5 roles : Admin, Receptionist, Doctor, Nurse and Patient. The program revolves around modular manager and a JSON persistence layer that centralizes patient profiles, medical records, appointments , staff shifts, remarks from doctors, requests from patients , assigninment of medication along with audit logging and backups. The system demonstrates many key programming concepts such as object-oriented design, robust validation rules, seperate role-based pages and unit testing for core modules.
---

## **Key Highlights**

* **Role-Based Access System**
  Custom dashboards and permissions for Admin, Doctor, Nurse, Receptionist, and Patient.

* **Patient Management**
  Create, view, edit, and delete patient profiles and medical records.

* **Appointment Scheduling**
  Simplify appointment creation and updates across different roles.

* **Shift Scheduling**
  Manage and visualize healthcare staff shift allocations.

* **Remarks & Observation Logging**
  Nurses and doctors can log remarks for ongoing patient care.

* **Streamlit Dashboard**
  Interactive UI for non-technical users with instant data feedback.

* **Data Persistence**
  Local JSON/CSV data storage (can be extended to SQL/NoSQL databases).

* **Modular Codebase**
  Clean separation between roles and functionalities under the `/app` directory.


Features Contained In This Application

Admin Management
- Create/update/remove user accounts for all roles
- View audit log of actions and trigger one‑click data backups
- Manage roster generation and data housekeeping tasks

Doctor Module
- View and edit assigned patient profiles and medical records
- Add typed remarks (mood, pain_level, dietary, observation, general) with timestamps
- Update appointment status (scheduled, completed, cancelled, no-show)
- Review medications and treatment notes per patient record

Nurse Module
- Create/update patient records, vitals, and day‑to‑day observations
- Assign or edit medications on the latest record
- Manage and update appointment details with doctors
- View own shifts and workload overview

Receptionist Module
- Register new patients and update demographics/contacts
- Create, update, or cancel appointments (by patient/doctor/date)
- Search and list patients with quick detail view
- Print/export daily appointment runsheet (planned enhancement)

Patient Module
- View personal profile, medical history, and upcoming appointments
- Read doctor/nurse remarks that are active (soft‑delete respected)
- Receive clearer appointment status and visit preparation notes

Appointment Management
- Create, edit, cancel appointments with ID counters
- List appointments by day/patient/doctor
- Enforce valid status lifecycle and required date/time fields
- Simple search helpers for front desk operations

Shift Scheduling
- Define staff shifts (day, start_time, end_time, remark)
- Assign shifts to nurses/doctors and view weekly rosters
- Store shifts in JSON alongside role data

Remarks & Observations
- PatientRemark model with soft‑delete and last_modified timestamp
- Typed categories to standardise documentation quality
- Doctor/Nurse authorship retained for traceability

Logging & Backup
- Append actions to data/audit.log
- Timestamped backups: carelog/backup/msms_backup_YYYYMMDD_HHMMSS.json
- Aids recovery and coursework demonstration of engineering practice

Automated Testing
- Unit tests with pytest (Arrange–Act–Assert)
- Core CRUD flows verified for profiles, records, remarks, and appointments
- Temporary JSON path used in tests to avoid polluting real data

Function Explanation
search_patient_by_name(name) – Find patient(s) by name for front‑desk and clinical use.  
view_patient_details_by_doctor(doctor_id, patient_id) – Scoped patient detail for doctors.  
view_patient_records_doctor(doctor_id, patient_id) – Read medical records as a doctor.  
update_patient_record_doctor(doctor_id, record_id, **fields) – Edit record fields with checks.  
delete_patient_record_doctor(doctor_id, record_id) – Remove a record with safety validation.  
assign_medications(record_id, medications:list) – Assign meds to latest record.  
edit_medications(record_id, medications:list) – Replace meds on a record.  
remove_medication(record_id, med_name) – Remove a specific medication.  
list_medications(patient_id, per_record=True|False) – List meds per record or aggregated.  
add_remark(patient_id, doctor_id, remark_type, content) – Create a typed remark entry.  
edit_remark(remark_id, **fields) – Update content/type; sets last_modified timestamp.  
delete_remark(remark_id) – Soft‑delete (is_active=False) to preserve auditability.  
create_appointment(p_id, d_id, date, time, remark) – Create appointment with new ID.  
update_appointment(appt_id, **fields) – Update date/time/remark/doctor linkage.  
update_appointment_status(appt_id, status) – Enforce allowed statuses only.  
cancel_appointment(appt_id) – Mark as cancelled; free slot for reschedule.  
setup_logging() / log_event(msg, level) – Append to audit log.  
BackupSystem() – Create time‑stamped JSON backup under carelog/backup.  
hash_password(pw) / check_password(pw, hash) – bcrypt‑ready helpers for secure auth.

## **Project Structure**

```bash
carelog/
│
├── app/
│   ├── admin.py              # Admin dashboard logic
│   ├── doctor.py             # Doctor module for patient diagnosis management
│   ├── nurse.py              # Nurse module for remarks, patient & appointment management
│   ├── receptionist.py       # Receptionist interface for appointment handling
│   ├── patient.py            # Patient record management
│   ├── schedule.py           # Appointment scheduling system
│   ├── shift_schedule.py     # Shift and roster management
│   ├── remark.py             # Remarks logging and tracking
│   ├── user.py               # User authentication and access control
│   ├── utils.py              # Shared utility functions
│   └── __init__.py
│
├── main.py                   # Main Streamlit entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── .gitignore
```
Design Considerations 

    Object‑Oriented Design – Users, PatientRecord, PatientAppointment, PatientRemark, Shift are explicit models for clarity and reuse.  

    Unique IDs – Auto‑increment counters for patients, staff, records, remarks, appointments ensure stable references and predictable persistence.  

    Validation Rules – Password strength (>=8 chars, upper, digit), email format with TLD, Malaysian contact pattern; constrained appointment statuses; typed remark categories; field type checks for lists/floats.  

    JSON Persistence – Lightweight local database (data/msms.json). Robust to restarts and easy to inspect for marking. Backups enable quick recovery.  

    Linked Records – Patients ↔ Records ↔ Appointments ↔ Staff maintained with role‑specific views; remarks and medications tied to the latest record with traceability. 

    User Interaction – Role‑based Streamlit pages (tabs/forms/tables) keep workflows simple and discoverable for non‑technical users. 

    Scalable – Modular managers make it easy to add export, analytics dashboards, or swap JSON for SQLite/PostgreSQL/Firebase later. 

    Automated Testing – Pytest validates core behaviours and guards against regressions. 

    Logging & Backup – Engineering hygiene for auditability and recovery are first‑class.
---

## **User Roles & Permissions**

| Role             | Capabilities                                                  |
| ---------------- | ------------------------------------------------------------- |
| **Admin**        | Full system access — manage users, appointments, and data     |
| **Doctor**       | View/edit patient medical info, add remarks                   |
| **Nurse**        | Manage appointments, update remarks, maintain patient records |
| **Receptionist** | Book and update appointments                                  |
| **Patient**      | View upcoming appointments and medical history                |

---

## **Testing**

CareLog supports unit and integration testing using **pytest**.

### Run All Tests:

```bash
pytest -v
```

### Example Test Structure:

```python
# tests/test_patient.py
def test_create_patient_record():
    patient = Patient("John Doe", "12345", "Cold")
    assert patient.name == "John Doe"
```

---

## **Software Architecture**

```text
User Interface (Streamlit)
        │
        ▼
Role-Based Controllers (admin.py, doctor.py, nurse.py, etc.)
        │
        ▼
Core Logic Modules (schedule.py, remark.py, shift_schedule.py)
        │
        ▼
Data Layer (utils.py, local JSON/CSV storage)
```

Modular MVC-like structure for maintainability and scalability
Easy migration to database-based systems (SQLite, PostgreSQL, Firebase, etc.)

---

## **Dependencies**

Here are common dependencies used in `requirements.txt` (ensure these are installed):

```txt
streamlit
streamlit-chatbox
bcrypt
pandas
numpy
pytest
python-dateutil
```

To export your exact project dependencies:

```bash
pip freeze > requirements.txt
```

---

## **Best Practices Implemented**

* Follows **PEP8** Python coding standards
* Uses **modular and reusable components**
* Includes **comments and docstrings** for maintainability
* Implements **data validation and error handling**
* Designed for **expandability** (database integration or authentication APIs)


**GitHub Link:**
* https://github.com/leejunming35622792/FIT1056-Sem2-2025/tree/project