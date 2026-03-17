from datetime import datetime

from . import db


class MemoryPage(db.Model):
    __tablename__ = "memory_pages"

    id = db.Column(db.Integer, primary_key=True)
    page_number = db.Column(db.Integer, nullable=False, unique=True)
    loaded_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, nullable=True)
    access_count = db.Column(db.Integer, nullable=False, default=0)
    in_memory = db.Column(db.Boolean, nullable=False, default=False)

    def touch(self, in_memory=True, increment=True):
        now = datetime.utcnow()
        if self.access_count is None:
            self.access_count = 0
        if not self.loaded_at:
            self.loaded_at = now
        self.last_accessed = now
        if increment:
            self.access_count += 1
        self.in_memory = in_memory

    def to_dict(self):
        return {
            "id": self.id,
            "page_number": self.page_number,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "in_memory": self.in_memory,
        }
