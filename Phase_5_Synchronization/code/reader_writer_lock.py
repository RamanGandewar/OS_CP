import threading
from datetime import datetime

from .mutex_manager import SYNC_MONITOR


class ReaderWriterLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.read_ready = threading.Condition(self.lock)
        self.readers = 0
        self.writer_active = False
        self.waiting_writers = 0

    def acquire_read(self, user_id, report_id):
        with self.read_ready:
            while self.writer_active or self.waiting_writers > 0:
                self.read_ready.wait()
            self.readers += 1
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Reader {user_id} opened report {report_id}")
        return {"success": True, "mode": "READ", "active_readers": self.readers}

    def release_read(self, user_id, report_id):
        with self.read_ready:
            self.readers -= 1
            if self.readers == 0:
                self.read_ready.notify_all()
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Reader {user_id} released report {report_id}")

    def acquire_write(self, user_id, report_id):
        with self.read_ready:
            self.waiting_writers += 1
            while self.writer_active or self.readers > 0:
                self.read_ready.wait()
            self.waiting_writers -= 1
            self.writer_active = True
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Writer {user_id} acquired exclusive report access for {report_id}")
        return {"success": True, "mode": "WRITE"}

    def release_write(self, user_id, report_id):
        with self.read_ready:
            self.writer_active = False
            self.read_ready.notify_all()
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Writer {user_id} released exclusive report access for {report_id}")
