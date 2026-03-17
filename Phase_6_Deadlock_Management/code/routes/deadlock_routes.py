from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from Backend.models import DeadlockEvent, db
from Phase_6_Deadlock_Management.code.bankers_algorithm import BankersAlgorithm
from Phase_6_Deadlock_Management.code.deadlock_detector import DeadlockDetector
from Phase_6_Deadlock_Management.code.deadlock_recovery import DeadlockRecovery
from Phase_6_Deadlock_Management.code.deadlock_visualizer import DeadlockVisualizer
from Phase_6_Deadlock_Management.code.resource_manager import ResourceManager

deadlock_bp = Blueprint("deadlock", __name__)

PHASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PHASE_DIR / "output"

resource_manager = ResourceManager()
detector = DeadlockDetector(OUTPUT_DIR)
visualizer = DeadlockVisualizer(OUTPUT_DIR)
recovery = DeadlockRecovery()


def _payload():
    return request.get_json(silent=True) or {}


@deadlock_bp.route("/init-resources", methods=["POST"])
def init_resources():
    return jsonify(resource_manager.initialize_defaults())


@deadlock_bp.route("/reset", methods=["POST"])
def reset_state():
    resource_manager.initialize_defaults()
    resource_manager.reset_state()
    DeadlockEvent.query.delete()
    db.session.commit()
    return jsonify(resource_manager.get_state())


@deadlock_bp.route("/state", methods=["GET"])
def state():
    resource_manager.initialize_defaults()
    snapshot = resource_manager.get_state()
    snapshot["events"] = [event.to_dict() for event in DeadlockEvent.query.order_by(DeadlockEvent.id.desc()).limit(20).all()]
    snapshot["visualization"] = visualizer.current_view()
    return jsonify(snapshot)


@deadlock_bp.route("/scenario/create", methods=["POST"])
def create_deadlock_scenario():
    resource_manager.initialize_defaults()
    resource_manager.reset_state()

    steps = [
        resource_manager.request_resource("P1", "R1_DB", grant=True),
        resource_manager.request_resource("P2", "R2_REPORT", grant=True),
        resource_manager.request_resource("P1", "R2_REPORT", grant=False),
        resource_manager.request_resource("P2", "R1_DB", grant=False),
    ]

    detection = detector.detect_deadlock(record_event=True)
    return jsonify({"message": "Deadlock scenario created", "steps": steps, "detection": detection})


@deadlock_bp.route("/detect", methods=["GET"])
def detect():
    resource_manager.initialize_defaults()
    return jsonify(detector.detect_deadlock(record_event=True))


@deadlock_bp.route("/banker-check", methods=["POST"])
def banker_check():
    resource_manager.initialize_defaults()
    payload = _payload()
    snapshot = resource_manager.get_state()
    banker = BankersAlgorithm(snapshot["resources"], snapshot["allocations"])
    process_id = str(payload.get("process_id", "P3"))
    request_map = payload.get("request") or {"R1_DB": 1, "R4_PDF": 1}
    result = banker.request_resources(process_id, request_map)
    safe, sequence = banker.is_safe_state()
    result["current_safe_state"] = safe
    result["current_safe_sequence"] = sequence
    return jsonify(result)


@deadlock_bp.route("/recover", methods=["POST"])
def recover_deadlock():
    payload = _payload()
    processes = payload.get("processes")
    if not processes:
        detection = detector.detect_deadlock(record_event=False)
        processes = detection.get("processes", [])

    if not processes:
        return jsonify({"message": "No deadlocked processes to recover", "recovered": False})

    result = recovery.recover(processes)
    state_snapshot = resource_manager.get_state()
    return jsonify({"recovered": True, "result": result, "state": state_snapshot})


@deadlock_bp.route("/events", methods=["GET"])
def events():
    return jsonify([event.to_dict() for event in DeadlockEvent.query.order_by(DeadlockEvent.id.desc()).limit(50).all()])


@deadlock_bp.route("/graph", methods=["GET"])
def graph():
    graph_path = OUTPUT_DIR / "resource_allocation_graph.png"
    if not graph_path.exists():
        visualizer.current_view()
    if not graph_path.exists():
        return jsonify({"error": "Graph image not available"}), 404
    return send_file(graph_path, mimetype="image/png")
