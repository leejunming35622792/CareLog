import csv

def export_report(self, kind, out_path):
    """Exports a log to a CSV file."""
    print(f"Exporting {kind} report to {out_path}...")
    # TODO: Use an if/elif block to select the correct data list based on 'kind'.
    if kind == "finance":
        data_to_export = self.finance_log
        headers = ["student_id", "amount", "method", "timestamp"]
    elif kind == "attendance":
        data_to_export = self.attendance
        headers = ["student_id", "course_id", "timestamp"]
    else:
        print("Error: Unknown report type.")
        return
    
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_to_export)

    # TODO: Use Python's 'csv' module to write the data.
    # Open the file, create a csv.DictWriter, write the header, then write all the rows.


    # ... inside ScheduleManager class ...