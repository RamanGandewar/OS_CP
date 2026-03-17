from datetime import datetime

from . import db


class ThreadRecord(db.Model):
    __tablename__ = "threads"

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    thread_name = db.Column(db.String(120), nullable=False)
    thread_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="READY")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cpu_time = db.Column(db.Float, nullable=False, default=0.0)
    memory_used = db.Column(db.Float, nullable=False, default=0.0)
    terminated_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        runtime_seconds = 0.0
        if self.created_at:
            end = self.terminated_at or datetime.utcnow()
            runtime_seconds = max(0.0, (end - self.created_at).total_seconds())

        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "thread_name": self.thread_name,
            "thread_type": self.thread_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "cpu_time": round(self.cpu_time, 4),
            "memory_used": round(self.memory_used, 4),
            "terminated_at": self.terminated_at.isoformat() if self.terminated_at else None,
            "runtime_seconds": round(runtime_seconds, 2),
        }
