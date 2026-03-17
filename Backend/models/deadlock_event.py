from datetime import datetime

from . import db


class DeadlockEvent(db.Model):
    __tablename__ = "deadlock_events"

    id = db.Column(db.Integer, primary_key=True)
    detected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    processes_involved = db.Column(db.String(255), nullable=False)
    resources_involved = db.Column(db.String(255), nullable=False)
    resolution_action = db.Column(db.String(255), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "processes_involved": self.processes_involved,
            "resources_involved": self.resources_involved,
            "resolution_action": self.resolution_action,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
