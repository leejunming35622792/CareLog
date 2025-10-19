def search_record(self, p_id, record_id):
        record_dict = {}
        for record in self.records:
            if record_id == record.pr_record_id:
                record_dict = {
                    "Record ID": record.pr_record_id,
                    "Patient ID": record.p_id,
                    "Date": record.pr_timestamp,
                    "Conditions": ", ".join(record.pr_conditions.keys()),
                    # "Conditions": ", ".join([f"{condition}: {severity}" for condition, severity in record.pr_conditions.items()]),
                    "Medications": record.pr_medications,
                    "Billings": record.pr_billings,
                    "Prediction Result": record.pr_prediction_result,
                    "Confidence Score": record.pr_confidence_score,
                    "Remark": record.pr_remark,
                }
        return record_dict