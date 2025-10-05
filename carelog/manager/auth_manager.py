"""Handles login logic"""
# --- Login ---
def check_credentials(self, staff, username, password):
    # Map each role to its user-password dict
    accounts = {
        "Patient": {p.username: p.password for p in self.patients},
        "Doctor": {d.username: d.password for d in self.doctors},
        "Nurse": {n.username: n.password for n in self.nurses},
        "Receptionist": {r.username: r.password for r in self.receptionists},
        "Admin": {a.username: a.password for a in self.admins},
    }

    # Check if role exists
    if staff not in accounts:
        return False

    acc = accounts[staff]

    # Verify username and password
    if username in acc and acc[username].strip() == password:
        return staff
    else:
        return False

def create_account(self, role, user_obj):
    role = role.lower()
    if role == "patient":
        self.patients.append(user_obj)
        self.next_patient_id += 1
    elif role == "doctor":
        self.doctors.append(user_obj)
        self.next_doctor_id += 1
    elif role == "nurse":
        self.nurses.append(user_obj)
        self.next_nurse_id += 1
    elif role == "receptionist":
        self.receptionists.append(user_obj)
        self.next_receptionist_id += 1
    elif role == "admin":
        self.admins.append(user_obj)
        self.next_admin_id += 1
    self.save()

# def login_doctor(self,username,password):
#         doctor=next((d for d in self.doctors if d.username==username))
#         if doctor is None:
#             return False, "Doctor Not Found ", None
#         if doctor.password != password:
#             return False, "Incorrect Password"
        
#         return True, "Logic Successful", doctor