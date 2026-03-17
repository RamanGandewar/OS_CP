from flask import Blueprint, jsonify, request, session
from sqlalchemy import or_

from Backend.models import Customer, Enquiry, Invoice, Quotation, SalesOrder, User, db
from Phase_2_Process_Management.code.process_manager import create_background_process
from Phase_3_CPU_Scheduling.code.routes.scheduler_routes import scheduler
from Phase_4_Thread_Management.code.thread_manager import thread_manager
from Backend.utils.validation import parse_date, require_fields

crm_bp = Blueprint("crm", __name__)


def list_response(model, search_fields=None):
    query = model.query
    q = request.args.get("q", "").strip()
    if q and search_fields:
        filters = [field.ilike(f"%{q}%") for field in search_fields]
        query = query.filter(or_(*filters))
    return jsonify([item.to_dict() for item in query.order_by(model.id.desc()).all()])


@crm_bp.route("/users", methods=["GET"])
def list_users():
    return jsonify([user.to_dict() for user in User.query.order_by(User.id.asc()).all()])


@crm_bp.route("/customers", methods=["GET", "POST"])
def customers():
    if request.method == "GET":
        return list_response(Customer, [Customer.name, Customer.email, Customer.company])

    payload = request.get_json() or {}
    missing = require_fields(payload, ["name", "email", "phone", "company", "address"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    customer = Customer(**payload)
    db.session.add(customer)
    db.session.commit()
    validation_thread = thread_manager.submit_validation_job({"customer_id": customer.id, "operation": "customer-create"})
    return jsonify(customer.to_dict() | {"validation_thread": validation_thread}), 201


@crm_bp.route("/customers/<int:item_id>", methods=["PUT", "DELETE"])
def customer_detail(item_id):
    customer = db.session.get(Customer, item_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    if request.method == "DELETE":
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted"})

    payload = request.get_json() or {}
    for field in ["name", "email", "phone", "company", "address"]:
        if field in payload and payload[field] != "":
            setattr(customer, field, payload[field])
    db.session.commit()
    return jsonify(customer.to_dict())


@crm_bp.route("/enquiries", methods=["GET", "POST"])
def enquiries():
    if request.method == "GET":
        query = Enquiry.query
        q = request.args.get("q", "").strip()
        status = request.args.get("status", "").strip()
        if q:
            query = query.join(Customer).filter(
                or_(
                    Customer.name.ilike(f"%{q}%"),
                    Enquiry.product.ilike(f"%{q}%"),
                    Enquiry.description.ilike(f"%{q}%"),
                )
            )
        if status:
            query = query.filter(Enquiry.status == status)
        return jsonify([item.to_dict() for item in query.order_by(Enquiry.id.desc()).all()])

    payload = request.get_json() or {}
    missing = require_fields(payload, ["customer_id", "product", "description", "status"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if not db.session.get(Customer, payload["customer_id"]):
        return jsonify({"error": "Customer not found"}), 404

    if payload.get("assigned_to") and not db.session.get(User, payload["assigned_to"]):
        return jsonify({"error": "Assigned user not found"}), 404

    enquiry = Enquiry(**payload)
    db.session.add(enquiry)
    db.session.commit()
    auto_save_thread_record = thread_manager.start_auto_save(enquiry.id)
    return jsonify(enquiry.to_dict() | {"auto_save_thread": auto_save_thread_record.to_dict()}), 201


@crm_bp.route("/enquiries/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def enquiry_detail(item_id):
    enquiry = db.session.get(Enquiry, item_id)
    if not enquiry:
        return jsonify({"error": "Enquiry not found"}), 404

    if request.method == "GET":
        return jsonify(enquiry.to_dict())

    if request.method == "DELETE":
        db.session.delete(enquiry)
        db.session.commit()
        return jsonify({"message": "Enquiry deleted"})

    payload = request.get_json() or {}
    for field in ["customer_id", "product", "description", "status", "assigned_to"]:
        if field in payload and payload[field] != "":
            setattr(enquiry, field, payload[field])
    db.session.commit()
    return jsonify(enquiry.to_dict())


@crm_bp.route("/quotations", methods=["GET", "POST"])
def quotations():
    if request.method == "GET":
        query = Quotation.query
        q = request.args.get("q", "").strip()
        if q:
            query = query.filter(
                or_(
                    Quotation.quotation_number.ilike(f"%{q}%"),
                    Quotation.status.ilike(f"%{q}%"),
                )
            )
        return jsonify([item.to_dict() for item in query.order_by(Quotation.id.desc()).all()])

    payload = request.get_json() or {}
    missing = require_fields(payload, ["enquiry_id", "quotation_number", "amount", "valid_until", "status"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if not db.session.get(Enquiry, payload["enquiry_id"]):
        return jsonify({"error": "Enquiry not found"}), 404

    valid_until, error = parse_date(payload["valid_until"], "valid_until")
    if error:
        return jsonify({"error": error}), 400

    quotation = Quotation(
        enquiry_id=payload["enquiry_id"],
        quotation_number=payload["quotation_number"],
        amount=float(payload["amount"]),
        valid_until=valid_until,
        status=payload["status"],
    )
    db.session.add(quotation)
    db.session.commit()
    scheduled_task = scheduler.add_real_world_task("quotation_pdf", requested_by=session.get("user_id"))
    validation_thread = thread_manager.submit_validation_job({"quotation_id": quotation.id, "operation": "quotation-create"})
    return jsonify(quotation.to_dict() | {"scheduled_task": scheduled_task, "validation_thread": validation_thread}), 201


@crm_bp.route("/quotations/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def quotation_detail(item_id):
    quotation = db.session.get(Quotation, item_id)
    if not quotation:
        return jsonify({"error": "Quotation not found"}), 404

    if request.method == "GET":
        return jsonify(quotation.to_dict())

    if request.method == "DELETE":
        db.session.delete(quotation)
        db.session.commit()
        return jsonify({"message": "Quotation deleted"})

    payload = request.get_json() or {}
    for field in ["enquiry_id", "quotation_number", "amount", "status"]:
        if field in payload and payload[field] != "":
            setattr(quotation, field, payload[field])
    if "valid_until" in payload and payload["valid_until"] != "":
        valid_until, error = parse_date(payload["valid_until"], "valid_until")
        if error:
            return jsonify({"error": error}), 400
        quotation.valid_until = valid_until
    db.session.commit()
    return jsonify(quotation.to_dict())


@crm_bp.route("/sales-orders", methods=["GET", "POST"])
def sales_orders():
    if request.method == "GET":
        query = SalesOrder.query
        q = request.args.get("q", "").strip()
        if q:
            query = query.filter(
                or_(
                    SalesOrder.order_number.ilike(f"%{q}%"),
                    SalesOrder.status.ilike(f"%{q}%"),
                )
            )
        return jsonify([item.to_dict() for item in query.order_by(SalesOrder.id.desc()).all()])

    payload = request.get_json() or {}
    missing = require_fields(payload, ["quotation_id", "order_number", "order_date", "delivery_date", "status"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    quotation = db.session.get(Quotation, payload["quotation_id"])
    if not quotation:
        return jsonify({"error": "Quotation not found"}), 404
    if quotation.status != "Approved":
        return jsonify({"error": "Sales orders can only be created from approved quotations"}), 400

    order_date, order_error = parse_date(payload["order_date"], "order_date")
    delivery_date, delivery_error = parse_date(payload["delivery_date"], "delivery_date")
    if order_error or delivery_error:
        return jsonify({"error": order_error or delivery_error}), 400

    order = SalesOrder(
        quotation_id=payload["quotation_id"],
        order_number=payload["order_number"],
        order_date=order_date,
        delivery_date=delivery_date,
        status=payload["status"],
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@crm_bp.route("/sales-orders/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def sales_order_detail(item_id):
    order = db.session.get(SalesOrder, item_id)
    if not order:
        return jsonify({"error": "Sales order not found"}), 404

    if request.method == "GET":
        return jsonify(order.to_dict())

    if request.method == "DELETE":
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Sales order deleted"})

    payload = request.get_json() or {}
    for field in ["quotation_id", "order_number", "status"]:
        if field in payload and payload[field] != "":
            setattr(order, field, payload[field])
    if "order_date" in payload and payload["order_date"] != "":
        parsed, error = parse_date(payload["order_date"], "order_date")
        if error:
            return jsonify({"error": error}), 400
        order.order_date = parsed
    if "delivery_date" in payload and payload["delivery_date"] != "":
        parsed, error = parse_date(payload["delivery_date"], "delivery_date")
        if error:
            return jsonify({"error": error}), 400
        order.delivery_date = parsed
    db.session.commit()
    return jsonify(order.to_dict())


@crm_bp.route("/invoices", methods=["GET", "POST"])
def invoices():
    if request.method == "GET":
        query = Invoice.query
        q = request.args.get("q", "").strip()
        if q:
            query = query.filter(
                or_(
                    Invoice.invoice_number.ilike(f"%{q}%"),
                    Invoice.payment_status.ilike(f"%{q}%"),
                )
            )
        return jsonify([item.to_dict() for item in query.order_by(Invoice.id.desc()).all()])

    payload = request.get_json() or {}
    missing = require_fields(payload, ["sales_order_id", "invoice_number", "amount", "due_date", "payment_status"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if not db.session.get(SalesOrder, payload["sales_order_id"]):
        return jsonify({"error": "Sales order not found"}), 404

    due_date, error = parse_date(payload["due_date"], "due_date")
    if error:
        return jsonify({"error": error}), 400

    invoice = Invoice(
        sales_order_id=payload["sales_order_id"],
        invoice_number=payload["invoice_number"],
        amount=float(payload["amount"]),
        due_date=due_date,
        payment_status=payload["payment_status"],
    )
    db.session.add(invoice)
    db.session.commit()
    pdf_pid = create_background_process(
        user_id=session.get("user_id"),
        task_type="pdf",
        operation=f"invoice-pdf-{invoice.invoice_number}",
        priority=4,
        duration=2,
        payload={"invoice_number": invoice.invoice_number},
    )
    email_pid = create_background_process(
        user_id=session.get("user_id"),
        task_type="email",
        operation=f"invoice-email-{invoice.invoice_number}",
        priority=3,
        duration=2,
        payload={"invoice_number": invoice.invoice_number},
    )
    pdf_task = scheduler.add_real_world_task("quotation_pdf", requested_by=session.get("user_id"))
    email_task = scheduler.add_real_world_task("email_notification", requested_by=session.get("user_id"))
    sync_thread = thread_manager.submit_sync_job({"invoice_id": invoice.id, "operation": "invoice-sync"})
    return jsonify(
        invoice.to_dict()
        | {
            "pdf_process_pid": pdf_pid,
            "email_process_pid": email_pid,
            "pdf_task": pdf_task,
            "email_task": email_task,
            "sync_thread": sync_thread,
        }
    ), 201


@crm_bp.route("/customers/export", methods=["POST"])
def export_customers():
    scheduled_task = scheduler.add_real_world_task("customer_export", requested_by=session.get("user_id"))
    return jsonify({"message": "Customer export task queued", "scheduled_task": scheduled_task}), 201


@crm_bp.route("/invoices/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def invoice_detail(item_id):
    invoice = db.session.get(Invoice, item_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    if request.method == "GET":
        return jsonify(invoice.to_dict())

    if request.method == "DELETE":
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({"message": "Invoice deleted"})

    payload = request.get_json() or {}
    for field in ["sales_order_id", "invoice_number", "amount", "payment_status"]:
        if field in payload and payload[field] != "":
            setattr(invoice, field, payload[field])
    if "due_date" in payload and payload["due_date"] != "":
        parsed, error = parse_date(payload["due_date"], "due_date")
        if error:
            return jsonify({"error": error}), 400
        invoice.due_date = parsed
    db.session.commit()
    return jsonify(invoice.to_dict())
