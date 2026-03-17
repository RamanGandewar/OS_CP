from datetime import datetime

from . import db


class LockRecord(db.Model):
    __tablename__ = "locks"

    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(50), nullable=False)
    holder_user_id = db.Column(db.Integer, nullable=True)
    holder_process_id = db.Column(db.Integer, nullable=True)
    acquired_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lock_type = db.Column(db.String(30), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")

    def to_dict(self):
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "holder_user_id": self.holder_user_id,
            "holder_process_id": self.holder_process_id,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "lock_type": self.lock_type,
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "status": self.status,
        }
