class Shift:
    def __init__(self, shift_id, staff_id, day, start_time, end_time, remark):
        self.shift_id = shift_id
        self.staff_id = staff_id
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.remark = remark

    def create_shift_object(shift_id, staff_id, day, start_time, end_time, remark):
        return Shift(shift_id, staff_id, day, start_time, end_time, remark)
