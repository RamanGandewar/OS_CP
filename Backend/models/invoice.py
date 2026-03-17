from . import db


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey("sales_orders.id"), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(50), nullable=False, default="Pending")

    def to_dict(self):
        return {
            "id": self.id,
            "sales_order_id": self.sales_order_id,
            "order_number": self.sales_order.order_number if self.sales_order else None,
            "invoice_number": self.invoice_number,
            "amount": self.amount,
            "due_date": self.due_date.isoformat(),
            "payment_status": self.payment_status,
        }
