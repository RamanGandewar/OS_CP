import csv
import json
import time
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, send_file, stream_with_context

from .analytics_generator import AnalyticsGenerator
from .performance_report import PerformanceReport
from .unified_dashboard import UnifiedDashboard
from .websocket_server import DashboardWebSocketServer

phase_dir = Path(__file__).resolve().parents[1]
output_dir = phase_dir / "output"
analytics_dir = phase_dir / "analytics"
output_dir.mkdir(parents=True, exist_ok=True)
analytics_dir.mkdir(parents=True, exist_ok=True)

analytics_generator = AnalyticsGenerator(analytics_dir)
performance_report = PerformanceReport(output_dir)
dashboard_service = UnifiedDashboard(analytics_generator, performance_report)
websocket_server = DashboardWebSocketServer(dashboard_service.snapshot)

dashboard_bp = Blueprint("integration_dashboard", __name__)


@dashboard_bp.route("/snapshot", methods=["GET"])
def snapshot():
    return jsonify(dashboard_service.snapshot())


@dashboard_bp.route("/analytics/generate", methods=["POST"])
def generate_analytics():
    analytics_files = analytics_generator.generate_files()
    report_path = performance_report.generate_markdown()
    return jsonify({"analytics_files": analytics_files, "performance_report": str(report_path)})


@dashboard_bp.route("/export/csv", methods=["GET"])
def export_csv():
    snapshot = dashboard_service.snapshot()
    target = output_dir / "dashboard_export.csv"
    with target.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["section", "metric", "value"])
        for key, value in snapshot["overview"].items():
            writer.writerow(["overview", key, json.dumps(value)])
        writer.writerow(["analytics", "summary", json.dumps(snapshot["analytics"])])
        writer.writerow(["performance_report", "summary", json.dumps(snapshot["performance_report"])])
    return send_file(target, mimetype="text/csv", as_attachment=True, download_name="dashboard_export.csv")


@dashboard_bp.route("/report", methods=["GET"])
def report():
    report_path = performance_report.generate_markdown()
    return send_file(report_path, mimetype="text/markdown", as_attachment=True, download_name="system_performance_report.md")


@dashboard_bp.route("/stream", methods=["GET"])
def stream():
    interval = float(request.args.get("interval", 2))

    def event_stream():
        for _ in range(5):
            yield websocket_server.sse_message()
            time.sleep(max(interval, 0.5))

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
