import os
import sys
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import LockQueueEntry, LockRecord, db
from .sync_monitor import SyncMonitor

OUTPUT_DIR = ROOT_DIR / "Phase_5_Synchronization" / "output"
SYNC_MONITOR = SyncMonitor(OUTPUT_DIR, ROOT_DIR / "Backend" / "database" / "crm.db")


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-5-sync-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class MutexManager:
    def __init__(self):
        self.registry_lock = threading.RLock()
        self.quotation_locks = {}

    def edit_quotation(self, quotation_id, user_id, data):
        with self.registry_lock:
            lock = self.quotation_locks.setdefault(str(quotation_id), threading.Lock())

        if lock.acquire(blocking=False):
            self._mark_lock("quotation", quotation_id, user_id, os.getpid(), "MUTEX")
            try:
                SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] User {user_id} acquired quotation mutex {quotation_id}")
                return {"message": f"Quotation {quotation_id} locked and edited", "data": data}
            finally:
                lock.release()
                self._release_lock("quotation", quotation_id, user_id)
        else:
            self._queue_waiter("quotation", quotation_id, user_id, "MUTEX")
            SYNC_MONITOR.append_conflict_log(f"[{datetime.utcnow().isoformat()}] User {user_id} blocked on quotation {quotation_id}")
            return {"message": f"Quotation {quotation_id} is locked by another user", "queued": True}

    def _mark_lock(self, resource_type, resource_id, user_id, process_id, lock_type):
        app = _get_app()
        with app.app_context():
            record = LockRecord(
                resource_type=resource_type,
                resource_id=str(resource_id),
                holder_user_id=user_id,
                holder_process_id=process_id,
                lock_type=lock_type,
                status="ACTIVE",
            )
            db.session.add(record)
            db.session.commit()

    def _release_lock(self, resource_type, resource_id, user_id):
        app = _get_app()
        with app.app_context():
            record = LockRecord.query.filter_by(
                resource_type=resource_type,
                resource_id=str(resource_id),
                holder_user_id=user_id,
                status="ACTIVE",
            ).order_by(LockRecord.acquired_at.desc()).first()
            if record:
                record.status = "RELEASED"
                record.released_at = datetime.utcnow()
                db.session.commit()

    def _queue_waiter(self, resource_type, resource_id, user_id, lock_type):
        app = _get_app()
        with app.app_context():
            entry = LockQueueEntry(
                resource_type=resource_type,
                resource_id=str(resource_id),
                waiting_user_id=user_id,
                requested_lock_type=lock_type,
                status="WAITING",
            )
            db.session.add(entry)
            db.session.commit()
