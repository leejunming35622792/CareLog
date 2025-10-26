import datetime
import pandas as pd
from app.shift_schedule import Shift
#creates a new shift and adds it to the manager's shift list 
def create_shift(manager, shift_id, staff_choice, day, start_time, end_time, remark):
    success, msg = check_shift_field(manager, shift_id, staff_choice, day, start_time, end_time, remark)
    if not success:
        return success, msg
    
    else:
        start_time_str = start_time.strftime("%H:%M")
        end_time_str = end_time.strftime("%H:%M")
        new_shift = Shift.create_shift_object(shift_id, staff_choice, day, start_time_str, end_time_str, remark)
        manager.shifts.append(new_shift)
        manager.next_shift_id += 1
        manager.save()
        manager._save_data()
        return True, f"New Shift {new_shift.shift_id} for {new_shift.staff_id} is added"

# validates shift fields, ensures a staff ID is provided
def check_shift_field(manager, shift_id, staff_choice, day, start_time, end_time, remark):
    shift_id = manager.next_shift_id
    if not staff_choice:
        return False, "Please select or enter a staff ID"
    return True, ""
#Retrieves all shifts for a specidic role  
def get_all_shift(manager, role):
    if role == "receptionist":
        return manager.shifts
#converts a list of shifts into pandas DataFrame     
def shift_convert_df(shifts):
    return pd.DataFrame([{
        "Shift ID": s.shift_id,
        "Staff": f"{s.staff_id} - {getattr(s, 'staff_name', 'Unknown')}",
        "Day": s.day,
        "Start Time": s.start_time,
        "End Time": s.end_time,
        "Remark": s.remark
    } for s in shifts])