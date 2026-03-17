from datetime import datetime

from . import db


class DiskRequest(db.Model):
    __tablename__ = "disk_requests"

    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)
    track_number = db.Column(db.Integer, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service_time = db.Column(db.Integer, nullable=False, default=0)
    algorithm_used = db.Column(db.String(30), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "request_type": self.request_type,
            "track_number": self.track_number,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "service_time": self.service_time,
            "algorithm_used": self.algorithm_used,
        }
