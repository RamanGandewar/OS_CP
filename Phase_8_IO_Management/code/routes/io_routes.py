from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from Phase_8_IO_Management.code.io_manager import IOManager

io_bp = Blueprint("io", __name__)
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"
io_manager = IOManager(OUTPUT_DIR)


def _payload():
    return request.get_json(silent=True) or {}


@io_bp.route("/monitor", methods=["GET"])
def monitor():
    io_manager.ensure_seed_requests()
    return jsonify(io_manager.get_monitor_payload())


@io_bp.route("/requests", methods=["POST"])
def add_request():
    io_manager.ensure_seed_requests()
    payload = _payload()
    record = io_manager.add_request(payload.get("request_type", "Custom Request"), int(payload.get("track_number", 0)))
    return jsonify(record), 201


@io_bp.route("/compare", methods=["POST"])
def compare():
    io_manager.ensure_seed_requests()
    payload = _payload()
    requests = payload.get("requests")
    current_head = int(payload.get("current_head", 50))
    comparison = io_manager.compare_algorithms(requests=requests, current_head=current_head)
    return jsonify(comparison)


@io_bp.route("/buffer/allocate", methods=["POST"])
def buffer_allocate():
    io_manager.ensure_seed_requests()
    payload = _payload()
    return jsonify(io_manager.allocate_buffer(payload.get("request_type", "upload"), int(payload.get("size", 64))))


@io_bp.route("/buffer/release", methods=["POST"])
def buffer_release():
    io_manager.ensure_seed_requests()
    payload = _payload()
    return jsonify(io_manager.release_buffer(int(payload.get("buffer_id", 0))))


@io_bp.route("/spool/enqueue", methods=["POST"])
def spool_enqueue():
    io_manager.ensure_seed_requests()
    payload = _payload()
    job = io_manager.enqueue_print(
        payload.get("job_type", "invoice"),
        payload.get("filename", "document.pdf"),
        int(payload.get("pages", 1)),
        payload.get("user_id"),
    )
    return jsonify(job), 201


@io_bp.route("/spool/process", methods=["POST"])
def spool_process():
    io_manager.ensure_seed_requests()
    return jsonify(io_manager.process_print())


@io_bp.route("/charts/<chart_name>", methods=["GET"])
def chart(chart_name):
    io_manager.ensure_seed_requests()
    chart_path = io_manager.chart_path(chart_name)
    if not chart_path.exists():
        io_manager.compare_algorithms()
    if not chart_path.exists():
        return jsonify({"error": "Chart not found"}), 404
    return send_file(chart_path, mimetype="image/png")
