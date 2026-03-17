from datetime import datetime

from . import db


class PrintQueueJob(db.Model):
    __tablename__ = "print_queue"

    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(30), nullable=False, default="QUEUED")

    def to_dict(self):
        return {
            "id": self.id,
            "job_type": self.job_type,
            "filename": self.filename,
            "pages": self.pages,
            "user_id": self.user_id,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "status": self.status,
        }
