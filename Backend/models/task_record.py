from datetime import datetime

from . import db


class TaskRecord(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    task_type = db.Column(db.String(30), nullable=False)
    burst_time = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_time = db.Column(db.DateTime, nullable=True)
    waiting_time = db.Column(db.Float, nullable=True)
    turnaround_time = db.Column(db.Float, nullable=True)
    response_time = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    algorithm_used = db.Column(db.String(20), nullable=True)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    remaining_time = db.Column(db.Integer, nullable=False)
    operation = db.Column(db.String(120), nullable=True)

    user = db.relationship("User", backref="tasks")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.remaining_time is None:
            self.remaining_time = self.burst_time

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time,
            "status": self.status,
            "algorithm_used": self.algorithm_used,
            "requested_by": self.requested_by,
            "remaining_time": self.remaining_time,
            "operation": self.operation,
        }
