def search_appt(self, chosen_appt_id):
        for appt in self.appointments:
            if appt.appt_id == chosen_appt_id:
                return {
                    "Appointment ID": appt.appt_id,
                    "Patient ID": appt.p_id,
                    "Doctor ID": appt.d_id,
                    "Appointment Date": appt.date,
                    "Appointment Time": appt.time,
                    "Appointment Status": appt.status,
                    "Remark": appt.remark
                }

def add_appointments(self, p_id, d_id, appt_date, appt_time, appt_remark):
        appt_id = f"AAPT{self.next_appt_id:04d}"
        new_appt = PatientAppointment.create(appt_id, p_id, d_id, appt_date, appt_time, "Pending", appt_remark)
        self.appointments.append(new_appt)
        self.next_appt_id += 1
        self._save_data()
        return True

def view_upcoming_appointments(self,username):
        doctor=next((d for d in self.doctors if d.username ==username), None)
        if doctor is None:
            return False, "No Doctor Found", None
        now = datetime.datetime.now()
        upcoming: list[dict]=[]

        for appt in self.appointments:
            if appt.doctor==doctor.d_id:
                try:
                    appt_dt=datetime.datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
                    if appt_dt >= now:
                        patient = self.get_patient_by_id(appt.patient)
                        upcoming.append(
                            {
                            "appt_id": appt.appt_id,
                            "patient_id": appt.patient,
                            "patient_name": patient.name if patient else "Unknown",
                            "date": appt.date,
                            "time": appt.time,
                            "status": appt.appt_status,
                            "remark": appt.appt_remark,
                            }
                        )
                except ValueError:
                    continue
        upcoming.sort(key=lambda x: f"{x['date']} {x['time']}")
        return True, f"Found {len(upcoming)} upcoming appointments", upcoming

def edit_appointments(self, appt_id, d_id, appt_date, appt_time, appt_remark):
        for appt in self.appointments:
            if appt.appt_id == appt_id:
                if d_id:
                    appt.d_id = d_id
                if appt_date:
                    appt.date = appt_date
                if appt_time:
                    appt.time = appt_time
                if appt_remark:
                    appt.remark = appt_remark
            return True
        
def delete_appointments(self, appt_id):
        self.appointments = [appt for appt in self.appointments if appt.appt_id != appt_id]
        return True