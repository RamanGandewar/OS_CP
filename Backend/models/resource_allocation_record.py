from . import db


class ResourceAllocationRecord(db.Model):
    __tablename__ = "resource_allocation"

    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    allocated_count = db.Column(db.Integer, nullable=False, default=0)
    requested_count = db.Column(db.Integer, nullable=False, default=0)

    resource = db.relationship("ResourceRecord", backref="allocations")

    def to_dict(self):
        return {
            "id": self.id,
            "process_id": self.process_id,
            "resource_id": self.resource_id,
            "resource_name": self.resource.resource_name if self.resource else None,
            "allocated_count": self.allocated_count,
            "requested_count": self.requested_count,
        }
