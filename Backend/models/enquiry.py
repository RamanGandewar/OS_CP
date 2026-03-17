from datetime import datetime

from . import db


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    product = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Open")
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    quotations = db.relationship("Quotation", backref="enquiry", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "product": self.product,
            "description": self.description,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "assigned_user": self.assignee.username if self.assignee else None,
            "created_at": self.created_at.isoformat(),
        }
