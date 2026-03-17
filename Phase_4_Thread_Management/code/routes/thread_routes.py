from flask import Blueprint, jsonify, request

from Phase_4_Thread_Management.code.thread_manager import thread_manager

thread_bp = Blueprint("thread", __name__)


@thread_bp.route("/monitor", methods=["GET"])
def monitor():
    return jsonify(thread_manager.get_monitor_payload())


@thread_bp.route("/auto-save", methods=["POST"])
def start_auto_save():
    payload = request.get_json() or {}
    record = thread_manager.start_auto_save(int(payload["enquiry_id"]))
    return jsonify(record.to_dict()), 201


@thread_bp.route("/report-job", methods=["POST"])
def report_job():
    payload = request.get_json() or {}
    record = thread_manager.submit_report_job(payload)
    return jsonify(record), 201


@thread_bp.route("/validation-job", methods=["POST"])
def validation_job():
    payload = request.get_json() or {}
    record = thread_manager.submit_validation_job(payload)
    return jsonify(record), 201


@thread_bp.route("/sync-job", methods=["POST"])
def sync_job():
    payload = request.get_json() or {}
    record = thread_manager.submit_sync_job(payload)
    return jsonify(record), 201


@thread_bp.route("/stop/<thread_name>", methods=["POST"])
def stop_thread(thread_name):
    stopped = thread_manager.stop_thread(thread_name)
    return jsonify({"stopped": stopped, "thread_name": thread_name})
