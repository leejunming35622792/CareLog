import pandas as pd
from app.shift_schedule import Shift

def create_shift(manager, shift_id, staff_choice, day, start_time, end_time, remark):
    start_time = start_time.isoformat()
    end_time = start_time.isoformat()

    success, msg = check_shift_field(manager, shift_id, staff_choice, day, start_time, end_time, remark)

    if not success:
        return success, msg
    
    else:
        new_shift = Shift.create_shift_object(shift_id, staff_choice, day, start_time, end_time, remark)
        manager.shifts.append(new_shift)
        manager.next_shift_id += 1
        return True, f"New Shift {new_shift.shift_id} for {new_shift.staff_id} is added"


def check_shift_field(manager, shift_id, staff_choice, day, start_time, end_time, remark):
    shift_id = manager.next_shift_id
    if not staff_choice:
        return False, "Please select or enter a staff ID"
    
def get_all_shift(manager, role):
    if role == "receptionist":
        return manager.shifts
    
def shift_convert_df(shifts):
    return pd.DataFrame([{
        "Shift ID": s.shift_id,
        "Staff": f"{s.staff_id} - {getattr(s, 'staff_name', 'Unknown')}",
        "Day": s.day,
        "Start Time": s.start_time,
        "End Time": s.end_time,
        "Remark": s.remark
    } for s in shifts])