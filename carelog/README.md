# **CareLog — Streamlit-Based Healthcare Management System**

> *An integrated digital healthcare management platform for hospitals and clinics, built using **Python** and **Streamlit**. Designed to simplify and centralize operations for **admins**, **doctors**, **nurses**, **receptionists**, and **patients** through secure, role-based access.*

---

## **Overview**
The CareLog application is a Streamlit-based workflow system for clinics that converts manual labour and tasks into 
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

---

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

---

## **Acknowledgements**

* Built for **Monash University Malaysia**
* Course: *FIT1056 – Introduction to Data Science and Programming (Sem 2, 2025)*
* Developed by: **Lee Jun Ming, Lim Seng Yang, Han Zun Ding, Ryan Hew Ka Sing** 
* Special thanks to lecturers and tutors for guidance and support
* Tools used: *Python, Streamlit, GitHub, VS Code*

---


**GitHub Link:**
* https://github.com/leejunming35622792/FIT1056-Sem2-2025/tree/project