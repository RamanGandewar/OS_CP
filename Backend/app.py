import sys
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from Backend.models import CacheStat, DiskRequest, MemoryPage, ProcessRecord, TaskRecord, ThreadRecord, db
from Backend.routes.auth import auth_bp
from Backend.routes.crm import crm_bp
from Backend.routes.report import report_bp
from Phase_2_Process_Management.code.routes.process_routes import process_bp
from Phase_3_CPU_Scheduling.code.routes.scheduler_routes import scheduler_bp
from Phase_4_Thread_Management.code.routes.thread_routes import thread_bp
from Phase_4_Thread_Management.code.thread_manager import thread_manager
from Phase_5_Synchronization.code.routes.sync_routes import sync_bp
from Phase_6_Deadlock_Management.code.routes.deadlock_routes import deadlock_bp
from Phase_7_Memory_Management.code.routes.memory_routes import memory_bp
from Phase_8_IO_Management.code.routes.io_routes import io_bp
from Phase_9_Integration_Dashboard.code.dashboard_api import dashboard_bp


def create_app():
    app = Flask(__name__)
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "database" / "crm.db"

    app.config["SECRET_KEY"] = "phase-1-basic-crm-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(crm_bp, url_prefix="/api")
    app.register_blueprint(process_bp, url_prefix="/api/processes")
    app.register_blueprint(scheduler_bp, url_prefix="/api/scheduler")
    app.register_blueprint(thread_bp, url_prefix="/api/threads")
    app.register_blueprint(sync_bp, url_prefix="/api/sync")
    app.register_blueprint(deadlock_bp, url_prefix="/api/deadlock")
    app.register_blueprint(memory_bp, url_prefix="/api/memory")
    app.register_blueprint(io_bp, url_prefix="/api/io")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(report_bp, url_prefix="/api/reports")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        latest_cache = CacheStat.query.order_by(CacheStat.timestamp.desc(), CacheStat.id.desc()).first()
        cache_ratio = round(latest_cache.hit_ratio, 2) if latest_cache else 0.0
        page_faults = MemoryPage.query.filter(MemoryPage.access_count > 0, MemoryPage.in_memory.is_(False)).count()
        return jsonify(
            {
                "status": "ok",
                "active_processes": ProcessRecord.query.filter(ProcessRecord.state != "TERMINATED").count(),
                "task_queue": TaskRecord.query.filter(TaskRecord.status != "COMPLETED").count(),
                "threads": ThreadRecord.query.filter(~ThreadRecord.status.in_(["TERMINATED", "COMPLETED", "FAILED"])).count(),
                "io_queue": DiskRequest.query.count(),
                "page_faults": page_faults,
                "cache_ratio": cache_ratio,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    thread_manager.start_system_threads()
    app.run(debug=True, use_reloader=False)
