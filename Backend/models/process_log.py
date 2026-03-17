from datetime import datetime

from . import db


class ProcessLog(db.Model):
    __tablename__ = "process_logs"

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False, index=True)
    previous_state = db.Column(db.String(20), nullable=True)
    new_state = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pid": self.pid,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "message": self.message,
            "logged_at": self.logged_at.isoformat(),
        }
