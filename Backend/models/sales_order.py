from datetime import date

from . import db


class SalesOrder(db.Model):
    __tablename__ = "sales_orders"

    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotations.id"), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=date.today)
    delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Created")

    invoices = db.relationship("Invoice", backref="sales_order", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "quotation_id": self.quotation_id,
            "quotation_number": self.quotation.quotation_number if self.quotation else None,
            "order_number": self.order_number,
            "order_date": self.order_date.isoformat(),
            "delivery_date": self.delivery_date.isoformat(),
            "status": self.status,
        }
