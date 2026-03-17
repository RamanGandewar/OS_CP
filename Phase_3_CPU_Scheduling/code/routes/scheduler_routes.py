from pathlib import Path

from flask import Blueprint, jsonify, request, send_file, session

from Phase_3_CPU_Scheduling.code.scheduler import CPUScheduler

scheduler_bp = Blueprint("scheduler", __name__)
scheduler = CPUScheduler()


@scheduler_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        return jsonify(scheduler.get_queue())

    payload = request.get_json() or {}
    task = scheduler.add_task(
        task_type=payload["task_type"],
        burst_time=int(payload["burst_time"]),
        priority=int(payload["priority"]),
        requested_by=session.get("user_id"),
        operation=payload.get("operation"),
    )
    return jsonify(task), 201


@scheduler_bp.route("/run", methods=["POST"])
def run_schedule():
    payload = request.get_json() or {}
    algorithm = (payload.get("algorithm") or "FCFS").upper()

    if algorithm == "FCFS":
        result = scheduler.fcfs_schedule()
    elif algorithm == "SJF":
        result = scheduler.sjf_schedule()
    elif algorithm == "PRIORITY":
        result = scheduler.priority_schedule()
    else:
        result = scheduler.round_robin_schedule(time_quantum=int(payload.get("time_quantum", 2)))

    return jsonify(result)


@scheduler_bp.route("/compare", methods=["GET"])
def compare():
    return jsonify(scheduler.compare_algorithms())


@scheduler_bp.route("/reset", methods=["POST"])
def reset():
    scheduler.reset_tasks()
    return jsonify({"message": "Task queue reset to PENDING state"})


@scheduler_bp.route("/gantt/<algorithm>", methods=["GET"])
def gantt_chart(algorithm):
    chart_path = Path("Phase_3_CPU_Scheduling") / "output" / f"{algorithm.lower()}_gantt_chart.png"
    absolute_path = Path(__file__).resolve().parents[3] / chart_path
    if not absolute_path.exists():
        return jsonify({"error": "Gantt chart not found. Run the scheduler first."}), 404
    return send_file(absolute_path, mimetype="image/png")
