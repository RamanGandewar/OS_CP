from flask import Blueprint, jsonify, request, session

from Backend.models import Enquiry, Invoice, Quotation, SalesOrder
from Phase_2_Process_Management.code.process_manager import create_background_process, wait_for_background_process
from Phase_3_CPU_Scheduling.code.routes.scheduler_routes import scheduler
from Phase_4_Thread_Management.code.thread_manager import thread_manager

report_bp = Blueprint("report", __name__)


@report_bp.route("/summary", methods=["GET"])
def summary():
    return jsonify(
        {
            "enquiries": [item.to_dict() for item in Enquiry.query.order_by(Enquiry.id.desc()).all()],
            "quotations": [item.to_dict() for item in Quotation.query.order_by(Quotation.id.desc()).all()],
            "sales_orders": [item.to_dict() for item in SalesOrder.query.order_by(SalesOrder.id.desc()).all()],
            "invoices": [item.to_dict() for item in Invoice.query.order_by(Invoice.id.desc()).all()],
        }
    )


@report_bp.route("/counts", methods=["GET"])
def counts():
    return jsonify(
        {
            "enquiries": Enquiry.query.count(),
            "quotations": Quotation.query.count(),
            "sales_orders": SalesOrder.query.count(),
            "invoices": Invoice.query.count(),
        }
    )


@report_bp.route("/generate", methods=["POST"])
def generate_report():
    payload = request.get_json() or {}
    wait_for_completion = bool(payload.get("wait", False))
    scheduled_task = scheduler.add_real_world_task("monthly_sales_report", requested_by=session.get("user_id"))
    thread_record = thread_manager.submit_report_job({"duration": payload.get("duration", 3), "scope": payload.get("scope", "all")})
    pid = create_background_process(
        user_id=session.get("user_id"),
        task_type="report",
        operation=payload.get("report_type", "crm-summary"),
        priority=int(payload.get("priority", 6)),
        duration=int(payload.get("duration", 3)),
        payload={"scope": payload.get("scope", "all")},
    )
    finished = wait_for_background_process(pid, timeout=10) if wait_for_completion else False
    return jsonify(
        {
            "message": "Report process started",
            "pid": pid,
            "finished": finished,
            "scheduled_task": scheduled_task,
            "thread_record": thread_record,
        }
    ), 201
