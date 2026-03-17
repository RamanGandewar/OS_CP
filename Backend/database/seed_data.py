import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app
from Backend.models import Customer, Enquiry, Invoice, Quotation, SalesOrder, User, db


with app.app_context():
    db.drop_all()
    db.create_all()

    users = []
    for idx in range(1, 6):
        user = User(
            username=f"user{idx}",
            email=f"user{idx}@crm.local",
            role="admin" if idx == 1 else "sales",
        )
        user.set_password("password123")
        users.append(user)
        db.session.add(user)

    customers = []
    for idx in range(1, 6):
        customer = Customer(
            name=f"Customer {idx}",
            email=f"customer{idx}@example.com",
            phone=f"98765000{idx}",
            company=f"Company {idx}",
            address=f"{idx} Market Street, City Center",
        )
        customers.append(customer)
        db.session.add(customer)

    db.session.flush()

    enquiries = []
    for idx in range(1, 6):
        enquiry = Enquiry(
            customer_id=customers[idx - 1].id,
            product=f"Product {idx}",
            description=f"Enquiry for Product {idx} with standard package.",
            status="Open" if idx < 3 else "Qualified",
            assigned_to=users[(idx - 1) % len(users)].id,
        )
        enquiries.append(enquiry)
        db.session.add(enquiry)

    db.session.flush()

    quotations = []
    quotation_statuses = ["Draft", "Approved", "Approved", "Sent", "Approved"]
    for idx in range(1, 6):
        quotation = Quotation(
            enquiry_id=enquiries[idx - 1].id,
            quotation_number=f"QT-2026-00{idx}",
            amount=10000 + (idx * 2500),
            valid_until=date.today() + timedelta(days=15 + idx),
            status=quotation_statuses[idx - 1],
        )
        quotations.append(quotation)
        db.session.add(quotation)

    db.session.flush()

    orders = []
    approved_quotations = [quote for quote in quotations if quote.status == "Approved"]
    for idx in range(1, 6):
        source_quote = approved_quotations[(idx - 1) % len(approved_quotations)]
        order = SalesOrder(
            quotation_id=source_quote.id,
            order_number=f"SO-2026-00{idx}",
            order_date=date.today() - timedelta(days=idx),
            delivery_date=date.today() + timedelta(days=7 + idx),
            status="Created" if idx < 3 else "Processing",
        )
        orders.append(order)
        db.session.add(order)

    db.session.flush()

    for idx in range(1, 6):
        invoice = Invoice(
            sales_order_id=orders[idx - 1].id,
            invoice_number=f"INV-2026-00{idx}",
            amount=15000 + (idx * 3000),
            due_date=date.today() + timedelta(days=10 + idx),
            payment_status="Pending" if idx % 2 else "Paid",
        )
        db.session.add(invoice)

    db.session.commit()
    print("Sample data inserted successfully.")
