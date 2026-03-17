import sqlite3
from collections import Counter
from pathlib import Path


class SyncMonitor:
    def __init__(self, output_dir, db_path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path)
        self.lock_log = self.output_dir / "lock_acquisition.log"
        self.conflict_log = self.output_dir / "conflict_resolution.log"

    def append_lock_log(self, message):
        self._append(self.lock_log, message)

    def append_conflict_log(self, message):
        self._append(self.conflict_log, message)

    def _append(self, path, message):
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(existing + message + "\n", encoding="utf-8")

    def get_monitor_payload(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        active_locks = connection.execute(
            "SELECT * FROM locks WHERE status = 'ACTIVE' ORDER BY acquired_at DESC"
        ).fetchall()
        queue_entries = connection.execute(
            "SELECT * FROM lock_queue ORDER BY requested_at DESC"
        ).fetchall()
        connection.close()

        return {
            "active_locks": [dict(row) for row in active_locks],
            "lock_queue": [dict(row) for row in queue_entries],
            "contention_counts": dict(Counter(f"{row['resource_type']}:{row['resource_id']}" for row in queue_entries)),
        }
