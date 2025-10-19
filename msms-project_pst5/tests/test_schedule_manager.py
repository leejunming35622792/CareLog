import sys, os, json, tempfile, shutil, pytest
from datetime import datetime
from PIL import Image

# Ensure app module is importable

from app.schedule import ScheduleManager
from app.student import StudentUser
from app.teacher import TeacherUser, Course, Lesson
from app.payment import Payment

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory with a mock JSON file."""
    data = {
    "students": [],
    "teachers": [],
    "staff": [],
    "courses": [],
    "attendance": [],
    "payment": [],
    "next_student_id": 1,
    "next_teacher_id": 1,
    "next_course_id": 1,
    "next_lesson_id": 1,
    "next_payment_id": 1
    }

    data_path = tmp_path / "msms.json"
    with open(data_path, "w") as f:
        json.dump(data, f)

    return str(data_path)


@pytest.fixture
def manager(temp_data_dir):
    """Initialize ScheduleManager with a temporary JSON path."""
    return ScheduleManager(data_path=temp_data_dir)

# ---------- Basic Data Loading ----------

def test_load_data_creates_empty_lists(manager):
    assert manager.students == []
    assert manager.teachers == []
    assert manager.courses == []
    assert manager.attendance == []
    assert manager.finance_log == []

# ---------- CRUD: Add Operations ----------

def test_add_student(manager):
    result = manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    assert result is True
    assert len(manager.students) == 1
    assert manager.students[0].name == "Alice"

def test_add_teacher(manager):
    result = manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    assert result is True
    assert len(manager.teachers) == 1
    assert manager.teachers[0].speciality == "Violin"

def test_add_course(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    new_course = manager.add_course("MS0001", "Music Theory", "Violin", "T0001")
    assert new_course.name == "Music Theory"
    assert len(manager.courses) == 1

def test_add_lesson(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    course = manager.add_course("MS0001", "Music Theory", "Violin", "T0001")
    result = manager.add_lesson(course.id, "Monday", "10:00", "Room 1", "Weekly")
    assert result is True
    assert len(course.lessons) == 1

# ---------- Attendance ----------

def test_add_attendance(manager):
    manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    manager.add_course("MS0001", "Piano Basics", "Piano", "T0001")
    result = manager.add_attendance("S0001", "MS0001")
    assert result is True
    assert len(manager.attendance) == 1

# ---------- Payment ----------

def test_add_payment(manager, tmp_path):
    img_path = tmp_path / "receipt.png"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(img_path)

    manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    payment = manager.add_payment("alice123", 100, "Cash", open(img_path, "rb"))
    assert payment is not False
    assert len(manager.finance_log) == 1


# ---------- Update ----------

def test_update_student(manager):
    manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    manager.update_student("alice123", "pw2", "S0001", "Alicia", "Violin", [])
    student = manager.students[0]
    assert student.password == "pw2"
    assert student.instrument == "Violin"

def test_update_teacher(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    result = manager.update_teacher("bobT", "pw3", "T0001", "Bobby", "Guitar")
    assert result is True
    teacher = manager.teachers[0]
    assert teacher.speciality == "Guitar"

def test_update_course(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    c = manager.add_course("MS0001", "Theory", "Violin", "T0001")
    result = manager.update_course(c.id, "Advanced Theory", "Cello", "T0001")
    assert result is True
    assert manager.courses[0].name == "Advanced Theory"

# ---------- Delete ----------

def test_delete_course(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    c = manager.add_course("MS0001", "Music", "Violin", "T0001")
    assert len(manager.courses) == 1
    manager.delete_course(c.id)
    assert len(manager.courses) == 0

# ---------- Search ----------

def test_search_student(manager):
    manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    result = manager.search_student("S0001")
    assert "Student Name" in result

def test_search_course_by_student_id(manager):
    manager.add_teacher("Bob", "bobT", "pw2", "Violin")
    c = manager.add_course("MS0001", "Music Theory", "Violin", "T0001")
    results = manager.search_course_by_student_id([c.id])
    assert results[0]["Course ID"] == c.id

# ---------- Export ----------

def test_export_report(manager, tmp_path):
    manager.add_student("Alice", "alice123", "pw1", "Piano", [])
    manager.add_attendance("S0001", "MS0001")

    out_path = tmp_path / "attendance.csv"
    manager.export_report("attendance", str(out_path))

    assert os.path.exists(out_path)
    with open(out_path) as f:
        lines = f.readlines()
    assert "student_id" in lines[0]

