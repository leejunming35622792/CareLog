import datetime

class Payment:
    def __init__(self, payment_id, student_id, amount, method, receipt, timestamp):
        self.payment_id = payment_id
        self.student_id = student_id
        self.amount = amount
        self.method = method
        self.receipt = receipt
        self.timestamp = timestamp

    @staticmethod
    def create_payment_object(payment_id, student_id, amount, method, receipt):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_payment = Payment(payment_id, student_id, amount, method, receipt, timestamp)
        return new_payment