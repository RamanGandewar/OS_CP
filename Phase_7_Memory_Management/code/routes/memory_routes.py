from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from Phase_7_Memory_Management.code.memory_monitor import MemoryMonitor

memory_bp = Blueprint("memory", __name__)
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"
memory_monitor = MemoryMonitor(OUTPUT_DIR)


def _payload():
    return request.get_json(silent=True) or {}


@memory_bp.route("/monitor", methods=["GET"])
def monitor():
    return jsonify(memory_monitor.get_monitor_payload())


@memory_bp.route("/report/page", methods=["POST"])
def load_report_page():
    payload = _payload()
    page_number = int(payload.get("page_number", 0))
    return jsonify(memory_monitor.load_report_page(page_number))


@memory_bp.route("/cache/customer", methods=["POST"])
def customer_cache():
    payload = _payload()
    return jsonify(memory_monitor.access_customer_cache(int(payload.get("customer_id", 1))))


@memory_bp.route("/cache/quotation", methods=["POST"])
def quotation_cache():
    payload = _payload()
    return jsonify(memory_monitor.access_quotation_cache(int(payload.get("quotation_id", 1))))


@memory_bp.route("/cache/user-preference", methods=["POST"])
def user_preference_cache():
    payload = _payload()
    return jsonify(memory_monitor.access_user_preference_cache(int(payload.get("user_id", 1))))


@memory_bp.route("/replacement/compare", methods=["POST"])
def compare_replacement():
    payload = _payload()
    reference_string = payload.get("reference_string")
    frame_count = int(payload.get("frame_count", 5))
    return jsonify(memory_monitor.simulate_reference_string(reference_string, frame_count))


@memory_bp.route("/allocator/allocate", methods=["POST"])
def allocator_allocate():
    payload = _payload()
    strategy = payload.get("strategy", "first_fit")
    size = int(payload.get("size", 50))
    return jsonify(memory_monitor.allocate_memory(strategy, size))


@memory_bp.route("/reset", methods=["POST"])
def reset():
    memory_monitor.reset()
    return jsonify({"message": "Memory monitor reset complete"})


@memory_bp.route("/charts/<chart_name>", methods=["GET"])
def chart(chart_name):
    chart_path = memory_monitor.chart_path(chart_name)
    if not chart_path or not chart_path.exists():
        memory_monitor._generate_charts()
    chart_path = memory_monitor.chart_path(chart_name)
    if not chart_path or not chart_path.exists():
        return jsonify({"error": "Chart not found"}), 404
    return send_file(chart_path, mimetype="image/png")
