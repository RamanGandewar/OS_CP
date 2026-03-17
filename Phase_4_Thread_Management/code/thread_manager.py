import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import Enquiry, ThreadRecord, db
from Phase_3_CPU_Scheduling.code.routes.scheduler_routes import scheduler
from .auto_save_thread import auto_save_thread
from .notification_thread import notification_thread
from .report_thread import report_generation_thread
from .thread_monitor import ThreadMonitor
from .thread_pool import ManagedThreadPool

OUTPUT_DIR = ROOT_DIR / "Phase_4_Thread_Management" / "output"
THREAD_MONITOR = ThreadMonitor(OUTPUT_DIR, ROOT_DIR / "Backend" / "database" / "crm.db")


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-4-thread-management-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class ThreadManager:
    # Centralized thread lifecycle manager with locking for thread-safe registry updates.
    def __init__(self):
        self.lock = threading.RLock()
        self.pool = ManagedThreadPool(max_workers=10)
        self.registry = {}
        self.background_started = False

    def start_system_threads(self):
        with self.lock:
            if self.background_started:
                return
            self.background_started = True
        self._start_daemon_thread("notification-daemon", "DAEMON", self._notification_loop)
        self._start_daemon_thread("session-timeout-daemon", "TIMER", self._session_timeout_loop)
        self._start_daemon_thread("data-sync-daemon", "DAEMON", self._data_sync_loop)

    def _start_daemon_thread(self, name, thread_type, target):
        stop_event = threading.Event()
        thread = threading.Thread(target=self._thread_wrapper, args=(target, stop_event, name, thread_type), daemon=True, name=name)
        thread.start()
        self._register_thread(thread, thread_type, "RUNNING")
        self.registry[thread.name] = {"thread": thread, "stop_event": stop_event, "type": thread_type}

    def start_auto_save(self, enquiry_id):
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._thread_wrapper,
            args=(lambda event: auto_save_thread(event, self._save_draft, enquiry_id), stop_event, f"autosave-{enquiry_id}", "TIMER"),
            daemon=True,
            name=f"autosave-{enquiry_id}",
        )
        thread.start()
        self._register_thread(thread, "TIMER", "RUNNING")
        self.registry[thread.name] = {"thread": thread, "stop_event": stop_event, "type": "TIMER"}
        return self._record_by_name(thread.name)

    def submit_validation_job(self, payload):
        return self._submit_pool_job("validation", self._validation_worker, payload)

    def submit_report_job(self, payload):
        return self._submit_pool_job("report", self._report_worker, payload)

    def submit_sync_job(self, payload):
        return self._submit_pool_job("sync", self._sync_worker_once, payload)

    def stop_thread(self, thread_name):
        with self.lock:
            item = self.registry.get(thread_name)
            if not item:
                return False
            item["stop_event"].set()
            return True

    def get_monitor_payload(self):
        self._refresh_metrics()
        payload = THREAD_MONITOR.get_summary()
        payload["native_threads"] = len(THREAD_MONITOR.get_native_threads())
        return payload

    def _submit_pool_job(self, name_prefix, target, payload):
        placeholder_name = f"{name_prefix}-{uuid.uuid4().hex[:8]}"
        record = self._create_placeholder_record(placeholder_name, "WORKER")
        future = self.pool.submit(self._pool_worker_wrapper, record["id"], target, payload, placeholder_name)
        with self.lock:
            self.registry[placeholder_name] = {"future": future, "stop_event": threading.Event(), "type": "WORKER"}
        return record

    def _pool_worker_wrapper(self, record_db_id, target, payload, thread_name):
        current = threading.current_thread()
        self._update_thread_identity(record_db_id, current)
        self._update_status(record_db_id, "RUNNING")
        start = time.perf_counter()
        try:
            target(payload)
            elapsed = time.perf_counter() - start
            self._update_metrics(record_db_id, elapsed)
            self._update_status(record_db_id, "COMPLETED")
        except Exception:
            elapsed = time.perf_counter() - start
            self._update_metrics(record_db_id, elapsed)
            self._update_status(record_db_id, "FAILED")
            raise
        finally:
            THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Worker thread {thread_name} finished")

    def _thread_wrapper(self, target, stop_event, name, thread_type):
        current = threading.current_thread()
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Thread {name} started as {thread_type}")
        target(stop_event)
        self._terminate_by_name(current.name)

    def _notification_loop(self, stop_event):
        notification_thread(stop_event, self._send_pending_notifications, interval=60)

    def _session_timeout_loop(self, stop_event):
        while not stop_event.wait(30):
            THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Session timeout checker heartbeat")

    def _data_sync_loop(self, stop_event):
        while not stop_event.wait(45):
            self._sync_worker_once({"source": "daemon"})

    def _report_worker(self, payload):
        report_generation_thread(payload, self._report_complete_callback)

    def _validation_worker(self, payload):
        time.sleep(2)
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Validation complete for {payload}")

    def _sync_worker_once(self, payload):
        time.sleep(2)
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Data sync complete for {payload}")

    def _send_pending_notifications(self):
        scheduler.add_real_world_task("email_notification")
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Notification daemon checked pending emails")

    def _save_draft(self, enquiry_id):
        app = _get_app()
        with app.app_context():
            enquiry = db.session.get(Enquiry, enquiry_id)
            if enquiry:
                enquiry.description = f"{enquiry.description}\n[Auto-saved at {datetime.utcnow().isoformat()}]"
                db.session.commit()
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Auto-saved enquiry draft {enquiry_id}")

    def _report_complete_callback(self, payload):
        scheduler.add_real_world_task("monthly_sales_report")
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Report thread completed payload {payload}")

    def _register_thread(self, thread, thread_type, status):
        app = _get_app()
        with app.app_context():
            record = ThreadRecord(
                thread_id=str(thread.native_id or thread.ident or uuid.uuid4()),
                thread_name=thread.name,
                thread_type=thread_type,
                status=status,
            )
            db.session.add(record)
            db.session.commit()
        THREAD_MONITOR.append_log(f"[{datetime.utcnow().isoformat()}] Registered thread {thread.name} ({thread_type})")

    def _create_placeholder_record(self, thread_name, thread_type):
        app = _get_app()
        with app.app_context():
            record = ThreadRecord(
                thread_id=f"pending-{uuid.uuid4().hex[:10]}",
                thread_name=thread_name,
                thread_type=thread_type,
                status="READY",
            )
            db.session.add(record)
            db.session.commit()
            return {
                "id": record.id,
                "thread_id": record.thread_id,
                "thread_name": record.thread_name,
                "thread_type": record.thread_type,
                "status": record.status,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "cpu_time": record.cpu_time,
                "memory_used": record.memory_used,
                "terminated_at": record.terminated_at.isoformat() if record.terminated_at else None,
                "runtime_seconds": 0.0,
            }

    def _update_thread_identity(self, record_db_id, thread):
        app = _get_app()
        with app.app_context():
            record = db.session.get(ThreadRecord, record_db_id)
            if not record:
                return
            record.thread_id = str(thread.native_id or thread.ident or record.thread_id)
            record.thread_name = thread.name
            db.session.commit()

    def _update_status(self, record_db_id, status):
        app = _get_app()
        with app.app_context():
            record = db.session.get(ThreadRecord, record_db_id)
            if not record:
                return
            record.status = status
            if status in {"COMPLETED", "TERMINATED", "FAILED"}:
                record.terminated_at = datetime.utcnow()
            db.session.commit()

    def _update_metrics(self, record_db_id, cpu_time):
        app = _get_app()
        with app.app_context():
            record = db.session.get(ThreadRecord, record_db_id)
            if not record:
                return
            record.cpu_time = cpu_time
            record.memory_used = self._estimate_memory()
            db.session.commit()

    def _terminate_by_name(self, thread_name):
        app = _get_app()
        with app.app_context():
            record = ThreadRecord.query.filter_by(thread_name=thread_name).order_by(ThreadRecord.id.desc()).first()
            if not record:
                return
            record.status = "TERMINATED"
            record.terminated_at = datetime.utcnow()
            db.session.commit()

    def _record_by_name(self, thread_name):
        app = _get_app()
        with app.app_context():
            record = ThreadRecord.query.filter_by(thread_name=thread_name).order_by(ThreadRecord.id.desc()).first()
            return record.to_dict() if record else None

    def _refresh_metrics(self):
        app = _get_app()
        with app.app_context():
            records = ThreadRecord.query.filter(ThreadRecord.status.in_(["RUNNING", "READY"])).all()
            for record in records:
                record.memory_used = self._estimate_memory()
            db.session.commit()

    def _estimate_memory(self):
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0


thread_manager = ThreadManager()
