from app.patient import PatientAppointment

# Working
def test_patient_appointment_accessors():
    appt = PatientAppointment.create(
        appt_id="A0009",
        p_id="P7777",
        d_id="D0001",
        appt_date="2025-11-01",
        appt_time="10:00",
        appt_status="scheduled",
        appt_remark="info"
    )
    assert appt.patient == "P7777"
    assert appt.doctor == "D0001"
    assert appt.appt_status == "scheduled"
    assert appt.appt_remark == "info"