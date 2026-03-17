from datetime import datetime

from . import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    enquiries = db.relationship("Enquiry", backref="customer", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
        }
