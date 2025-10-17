# app/admin_utils.py
import logging
import shutil
import datetime
import os

# ----- Logger ----- 
def init_logger(username):
    """
    Initializes a dedicated logger for a specific admin or user.
    Each user's logs are stored under data/logs/<username>/.
    """
    base_dir = f"data/logs/{username}/"
    os.makedirs(base_dir, exist_ok=True)

    # Create unique log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(base_dir, f"{username}_{timestamp}.log")

    # Remove existing logging handlers to avoid duplicate log entries
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure new logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )

    print(f"✅ Logging configured for '{username}'. File: {log_file}")


# ----- Backup ----- 
def backup_data(data_path="data/msms.json", backup_dir="data/backups"):
    """
    Creates a timestamped backup copy of the main msms.json data file.
    Used for data recovery in case of corruption or accidental deletion.
    """
    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate timestamp and destination filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"msms_backup_{timestamp}.json"
    backup_filepath = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy original JSON data file to backup directory
        shutil.copy(data_path, backup_filepath)

        # Log the backup event
        logging.info(f"Data successfully backed up to {backup_filepath}")
        return True
    except Exception as e:
        # Log any failure during the backup process
        logging.error(f"Failed to create backup: {e}")
        return False
