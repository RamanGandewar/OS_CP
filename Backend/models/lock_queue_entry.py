from datetime import datetime

from . import db


class LockQueueEntry(db.Model):
    __tablename__ = "lock_queue"

    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(50), nullable=False)
    waiting_user_id = db.Column(db.Integer, nullable=True)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="WAITING")
    requested_lock_type = db.Column(db.String(30), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "waiting_user_id": self.waiting_user_id,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "status": self.status,
            "requested_lock_type": self.requested_lock_type,
        }
