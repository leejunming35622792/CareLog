# pst2_main.py - The Persistent Application
# Lee Jun Ming 35622792
#FIT1056-Sem2-2025

import json
import datetime

# variable
DATA_FILE = "msms.json"
app_data = {}

# --- Core Persistence Engine ---
def load_data(path=DATA_FILE):
    global app_data

    try:
        with open(path, "r") as f:
            app_data = json.load(f)
            print("Data loaded successfully.")

    except FileNotFoundError:
        print("Data file not found. Initializing with default structure.")

        app_data = {
            "students": [],
            "teachers": [],
            "attendance": [],
            "next_student_id": 1,
            "next_teacher_id": 1
        }

def save_data(path=DATA_FILE):
    with open(path, "w") as f:
        json.dump(app_data, f, indent=4)
    print("Data saved successfully.")
