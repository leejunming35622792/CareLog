# app/admin_utils.py
import logging
import shutil
import datetime
import os

# ----- Logger ----- 
def init_logger(username):
    base_dir = f"data/logs/{username}/"
    os.makedirs(base_dir, exist_ok=True)

    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    log_file = os.path.join(base_dir, f"{username}_{timestamp}.log")

    # Remove any existing handlers (important!)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Now configure new logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )

    print(f"✅ Logging configured for '{username}'. File: {log_file}")


# ----- Backup ----- 
def backup_data(data_path="data/msms.json", backup_dir="data/backups"):
    """Creates a timestamped backup of the main data file."""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Formatting
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"msms_backup_{timestamp}.json"
    backup_filepath = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy the data_path to the backup_filepath.
        shutil.copy(data_path, backup_filepath)

        # Use the logging module to record this event.
        logging.info(f"Data successfully backed up to {backup_filepath}")
        return True
    except Exception as e:
        # Log any errors that occur during the backup process.
        logging.error(f"Failed to create backup: {e}")
        return False