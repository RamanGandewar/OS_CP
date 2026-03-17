from datetime import datetime

from . import db


class ProcessRecord(db.Model):
    __tablename__ = "processes"

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    state = db.Column(db.String(20), nullable=False, default="NEW")
    priority = db.Column(db.Integer, nullable=False, default=5)
    cpu_time = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime, nullable=True)
    parent_pid = db.Column(db.Integer, nullable=True)
    task_type = db.Column(db.String(50), nullable=False, default="session")
    operation = db.Column(db.String(120), nullable=True)

    user = db.relationship("User", backref="processes")

    def to_dict(self):
        return {
            "id": self.id,
            "pid": self.pid,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "system",
            "state": self.state,
            "priority": self.priority,
            "cpu_time": round(self.cpu_time, 4),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "terminated_at": self.terminated_at.isoformat() if self.terminated_at else None,
            "parent_pid": self.parent_pid,
            "task_type": self.task_type,
            "operation": self.operation,
        }
