from flask import Blueprint, jsonify, request, session

from Phase_2_Process_Management.code.process_manager import (
    create_background_process,
    get_monitor_payload,
    get_process_logs,
    wait_for_background_process,
)

process_bp = Blueprint("process", __name__)


@process_bp.route("/monitor", methods=["GET"])
def process_monitor():
    payload = get_monitor_payload()
    payload["logs"] = get_process_logs(limit=50)
    return jsonify(payload)


@process_bp.route("/logs", methods=["GET"])
def process_logs():
    limit = int(request.args.get("limit", 100))
    return jsonify(get_process_logs(limit=limit))


@process_bp.route("/background-task", methods=["POST"])
def trigger_background_task():
    payload = request.get_json() or {}
    user_id = session.get("user_id")
    task_type = payload.get("task_type", "report")
    operation = payload.get("operation", "manual-trigger")
    wait_for_child = bool(payload.get("wait", False))

    pid = create_background_process(
        user_id=user_id,
        task_type=task_type,
        operation=operation,
        priority=int(payload.get("priority", 5)),
        duration=int(payload.get("duration", 2)),
        payload=payload.get("payload", {}),
    )

    finished = wait_for_background_process(pid, timeout=10) if wait_for_child else False
    return jsonify({"pid": pid, "finished": finished, "task_type": task_type, "operation": operation}), 201
