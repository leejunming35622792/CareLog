import os
import shutil
import importlib

import pytest

DATA_SRC = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'msms.json')


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    # Create temp data directory with a copy of msms.json
    data_dir = tmp_path / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA_SRC, data_dir / 'msms.json')

    # Switch CWD to the tmp dir so ScheduleManager('data/msms.json') uses the temp copy
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Import modules fresh under this CWD
        for mod_name in [
            'app.schedule',
            'helper_manager.profile_manager',
            'helper_manager.record_manager',
            'helper_manager.medication_manager',
        ]:
            if mod_name in list(importlib.sys.modules.keys()):
                importlib.reload(importlib.import_module(mod_name))
            else:
                importlib.import_module(mod_name)
        yield
    finally:
        os.chdir(old_cwd)


def _get_manager():
    from app.schedule import ScheduleManager
    return ScheduleManager()


def test_view_doctor_details_ok():
    from helper_manager.profile_manager import view_doctor_details
    ok, msg, profile = view_doctor_details('doc')
    assert ok, msg
    assert profile['staff_id'].startswith('D')
    assert profile['name']
    assert profile['department']


def test_view_patient_details_by_doctor_ok():
    from helper_manager.profile_manager import view_patient_details_by_doctor
    ok, msg, info = view_patient_details_by_doctor('P0001')
    assert ok, msg
    assert info['patient_id'] == 'P0001'
    assert 'name' in info
    assert isinstance(info.get('previous_conditions', []), list)
    assert isinstance(info.get('medication_history', []), list)


def test_view_patient_records_doctor_ok():
    from helper_manager.record_manager import view_patient_records_doctor
    ok, msg, records = view_patient_records_doctor('P0001')
    assert ok, msg
    assert isinstance(records, list)
    assert len(records) >= 1


def test_update_patient_record_doctor_medical_only():
    from helper_manager.record_manager import update_patient_record_doctor
    # choose an existing record
    m = _get_manager()
    target = next((r for r in m.records if r.p_id == 'P0001'), None)
    assert target is not None, 'No record for P0001 in test data'

    # capture old remark
    old_remark = target.pr_remark

    ok, msg = update_patient_record_doctor(
        target.pr_record_id,
        conditions={'TestCondition': 'Low'},
        medications=['TestMed'],
        billings=123.45,
        prediction_result='TestResult',
        confidence_score=0.77,
    )
    assert ok, msg

    # reload and verify
    m2 = _get_manager()
    rec2 = next(r for r in m2.records if r.pr_record_id == target.pr_record_id)
    assert isinstance(rec2.pr_conditions, (dict, str))
    assert rec2.pr_medications
    assert float(rec2.pr_billings) == pytest.approx(123.45)
    assert str(rec2.pr_prediction_result) == 'TestResult'
    assert float(rec2.pr_confidence_score) == pytest.approx(0.77)
    # remark should remain unchanged
    assert rec2.pr_remark == old_remark


def test_delete_patient_record_doctor_temp():
    from helper_manager.record_manager import delete_patient_record_doctor
    from app.patient import PatientRecord

    m = _get_manager()
    # create a temporary record to delete
    temp_id = 'PRTESTDOC'
    m.records.append(PatientRecord(temp_id, 'P0001', '2025-10-22T00:00:00', '', [], 0.0, None, None, 'temp'))
    m.save()

    ok, msg, deleted_id = delete_patient_record_doctor(temp_id)
    assert ok, msg
    assert deleted_id == temp_id

    m2 = _get_manager()
    assert all(r.pr_record_id != temp_id for r in m2.records)


def test_medication_manager_assign_and_edit():
    from helper_manager.medication_manager import assign_medications, edit_medications, remove_medication, list_medications

    # assign with new_record
    ok, msg, pr_id = assign_medications('P0001', 'Amoxicillin', doctor_username='doc', instructions='Take with food', new_record=True)
    assert ok, msg
    assert pr_id

    # replace medications
    ok2, msg2 = edit_medications(pr_id, ['MedA', 'MedB'])
    assert ok2, msg2

    # remove one med
    ok3, msg3 = remove_medication(pr_id, 'MedA')
    assert ok3, msg3

    # list per record should include our PR id
    ok4, msg4, rows = list_medications('P0001', per_record=True)
    assert ok4, msg4
    assert any(row['record_id'] == pr_id for row in rows)



def test_search_patient_by_name_types():
    from helper_manager.profile_manager import search_patient_by_name
    ok, msg, results = search_patient_by_name("this_name_is_unlikely_to_exist_12345")
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    assert isinstance(results, list)

def test_view_patient_records_doctor_not_found():
    from helper_manager.record_manager import view_patient_records_doctor
    ok, msg, records = view_patient_records_doctor('P_DOES_NOT_EXIST')
    assert ok is False
    # records may be None or [], just ensure not a non-empty list
    assert not records

def test_update_patient_record_doctor_invalid_billings():
    from helper_manager.record_manager import update_patient_record_doctor
    m = _get_manager()
    target = next(iter(m.records), None)
    assert target is not None, "No records available for invalid billings test"
    ok, msg = update_patient_record_doctor(target.pr_record_id, billings="not-a-number")
    assert ok is False
    assert "billings" in msg.lower()

def test_delete_patient_record_doctor_not_found():
    from helper_manager.record_manager import delete_patient_record_doctor
    ok, msg, deleted_id = delete_patient_record_doctor('PR_DOES_NOT_EXIST')
    assert ok is False
    assert deleted_id is None
