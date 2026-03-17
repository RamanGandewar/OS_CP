from datetime import datetime

from . import db


class Quotation(db.Model):
    __tablename__ = "quotations"

    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey("enquiries.id"), nullable=False)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    valid_until = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Draft")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sales_orders = db.relationship("SalesOrder", backref="quotation", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "enquiry_id": self.enquiry_id,
            "enquiry_product": self.enquiry.product if self.enquiry else None,
            "quotation_number": self.quotation_number,
            "amount": self.amount,
            "valid_until": self.valid_until.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
