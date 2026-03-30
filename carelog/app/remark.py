import datetime
#PatientRemark class to handle remarks made by doctors on patients with its attributes and methods
class PatientRemark:
    def __init__ (self, remark_id:str, patient_id:int, doctor_id:int, timestamp:str, remark_type:str, content:str, last_modified:str, is_active: bool= True): 
        self.remark_id      =   remark_id
        self.patient_id     =   patient_id
        self.doctor_id      =   doctor_id
        self.timestamp      =   timestamp
        self.remark_type    =   remark_type
        self.content        =   content
        self.last_modified  =   last_modified
        self.is_active      =   is_active
    # String representation of the remark
    def __str__(self):
        return f"[{self.timestamp}]{self.remark_type.upper()}: {self.content}"
    # Convert remark to dictionary
    def to_dict(self) -> dict:
        return {
            "remark_id": self.remark_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "timestamp": self.timestamp,
            "remark_type": self.remark_type,
            "content": self.content,
            "is_active": self.is_active,
            "last_modified": self.last_modified
        }
    # create remark from dictionary of JSON persistence layer 
    @staticmethod
    def from_dict(data: dict):
        return PatientRemark(
            remark_id=data["remark_id"],
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            timestamp=data["timestamp"],
            remark_type=data["remark_type"],
            content=data["content"],
            is_active=data.get("is_active", True),
            last_modified=str(data.get("last_modified") or data.get("timestamp") or ""),
        )
    # Update remark content
    def update_content(self, new_content: str):
        """Update the remark content and track modification time"""
        self.content = new_content
        self.last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Deactivate remark
    def deactivate(self):
        """Soft delete the remark"""
        self.is_active = False
        self.last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")