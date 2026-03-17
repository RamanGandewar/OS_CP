from . import db


class ResourceRecord(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(50), nullable=False, unique=True)
    resource_type = db.Column(db.String(50), nullable=False)
    total_instances = db.Column(db.Integer, nullable=False)
    available_instances = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "total_instances": self.total_instances,
            "available_instances": self.available_instances,
        }
