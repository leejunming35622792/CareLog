import os, shutil, datetime, logging, json

# Global list to hold structured logs
systemlogs = []

def setup_logging(log_file="data/audit.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),                           # console
            logging.FileHandler(log_file, encoding="utf-8")    # file
        ]
    )

def log_event(event, level="INFO"):
    """Logs an event to memory (systemlogs) and audit.log"""
    level = level.upper()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = {"timestamp": timestamp, "level": level, "event": event}
    systemlogs.append(log_entry)   # keep in memory

    # standard logging (to console + file)
    if level == "INFO":
        logging.info(event)
    elif level == "ERROR":
        logging.error(event)
    elif level == "WARNING":
        logging.warning(event)

def get_recent_logs(n=10):
    """Return last n logs"""
    return systemlogs[-n:]

def view_users():
    from app.schedule import ScheduleManager
    """View all users"""
    users = [
        {"Type": "Doctor", "ID": d.id, "Name": d.name, "Username": d.username, "Gender": d.gender, "Address": d.address, "Email": d.email, "Contact": d.contact_num}
        for d in ScheduleManager.doctors
    ]
    return users

def BackupSystem():
    """Backup Database"""
    source_file = "data/msms.json"
    backup_dir = "carelog/backup"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"msms_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        shutil.copy(source_file, backup_path)
        log_event(f"Backup created at {backup_path} on {datetime.datetime.now().isoformat()}", "INFO")
    except Exception as e:
        log_event(f"Backup failed: {e}", "ERROR")