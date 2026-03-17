from datetime import datetime

from . import db


class CacheStat(db.Model):
    __tablename__ = "cache_stats"

    id = db.Column(db.Integer, primary_key=True)
    cache_type = db.Column(db.String(50), nullable=False)
    hits = db.Column(db.Integer, nullable=False, default=0)
    misses = db.Column(db.Integer, nullable=False, default=0)
    hit_ratio = db.Column(db.Float, nullable=False, default=0.0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "cache_type": self.cache_type,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hit_ratio,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
