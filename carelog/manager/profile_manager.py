def view_doctor_details(self, username):
        doctor = next((d for d in self.doctors if d.username == username), None)

        if doctor is None:
            return False, "Doctor Not Found", None
        
        # if doctor.password != password:
        #     return False, "Doctor Not Found", None
        
        profile= {
            "staff_id":doctor.d_id,
            "name":doctor.name,
            "email":doctor.email,
            "contact_num": doctor.contact_num,
            "address": doctor.address,
            "gender": doctor.gender,
            "date_of_birth": getattr(doctor,"date_of_birth",""),
            "department": doctor.department,
            "speciality": doctor.speciality,
            "date_joined": doctor.date_joined,
        }
        return True, "Profile Successfully Retrieved", profile

def view_patient_details_by_doctor(self,patient_id :int):
        patient=next((p for p in self.patients if p.p_id ==patient_id),None)
        if patient is None:
            return False,"Patient Not Found", None
        patient_records=[r for r in self.records if r.patient==patient_id]
        previous_conditions: list[str]= []
        medication_history: list[str]= []
        for record in patient_records:
            if getattr(record,"pr_conditions",None):
                previous_conditions.extend(record.pr_conditions)
            if hasattr(record,"pr_medications") and record.pr_medications:
                medication_history.extend(record.pr_medications)
        previous_conditions = list(set(previous_conditions))
        info = {
            "patient_id": patient.p_id,
            "name": patient.name,
            "gender": patient.gender,
            "date_of_birth": getattr(patient, "date_of_birth", ""),
            "previous_conditions": previous_conditions,
            "medication_history": medication_history,
            }
        return True, "Patient details retrieved successfully", info

def view_nurse_details(self, username, password):
        nurse = next((n for n in self.nurses if n.username == username), None)
        if nurse is None:
            return False, "Nurse not found", None
        if nurse.password != password:
            return False, "Incorrect password", None
        
        profile = {
            "staff_id": nurse.n_id,
            "name": nurse.name,
            "email": nurse.email,
            "contact_num": nurse.contact_num,
            "address": nurse.address,
            "gender": nurse.gender,
            "date_of_birth": getattr(nurse, "date_of_birth", ""),
            "department": nurse.department,
            "speciality": nurse.speciality,
            "date_joined": nurse.date_joined,
            "with_doctor": nurse.with_doctor
        }
        return True, "Profile successfully retrieved", profile

def view_patient_details_by_nurse(self, patient_id: int):
        patient = next((p for p in self.patients if p.p_id == patient_id), None)
        if patient is None:
            return False, "Patient not found", None
        info = {
            "patient_id": patient.p_id,
            "name": patient.name,
            "gender": patient.gender,
            "date_of_birth": getattr(patient, "date_of_birth", ""),
            "remarks": getattr(patient, "p_remark", [])
        }
        return True, "Patient details retrieved successfully", info

def search_and_select_profile(self):
        role = input("Search for (patient/doctor/nurse/receptionist): ").strip().lower()
        role_map = {
        "patient": (self.patients, "p_id"),
        "doctor": (self.doctors, "d_id"),
        "nurse": (self.nurses, "n_id"),
        "receptionist": (self.receptionists, "r_id"),
        }
        if role not in role_map:
            print("Invalid role. Please enter patient/doctor/nurse/receptionist.")
            return False, None

        items, id_attr = role_map[role]
        name_query = input("Enter name (partial is okay): ").strip().lower()
        matches = [obj for obj in items if name_query in getattr(obj, "name", "").lower()]

        if not matches:
            print(f"No {role} found matching '{name_query}'.")
            return False, None

        print(f"\nFound {len(matches)} {role}(s):")
        for obj in matches:
            pid = getattr(obj, id_attr)
            print(f"- {pid}: {obj.name}")

        selected_id = input(f"\nEnter the exact {role.capitalize()} ID to view (e.g., P0001/N0003): ").strip().upper()
        selected = next((o for o in matches if getattr(o, id_attr).upper() == selected_id), None)

        if not selected:
            print("No profile found with that ID in the above results.")
            return False, None

        print("\n--- Profile ---")
        for k, v in selected.__dict__.items():
            if k == "password":
                continue
            print(f"{k}: {v}")

        return True, selected
