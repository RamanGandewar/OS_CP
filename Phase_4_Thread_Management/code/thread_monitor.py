import os
import sqlite3
from collections import Counter
from pathlib import Path

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

class ThreadMonitor:
    def __init__(self, output_dir, db_path=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.output_dir / "thread_execution.log"
        self.db_path = Path(db_path) if db_path else None

    def append_log(self, message):
        existing = self.log_path.read_text(encoding="utf-8") if self.log_path.exists() else ""
        self.log_path.write_text(existing + message + "\n", encoding="utf-8")

    def get_summary(self):
        rows = self._fetch_rows()
        state_counts = Counter(row["status"] for row in rows)
        return {
            "active_count": sum(1 for row in rows if row["status"] not in {"TERMINATED", "COMPLETED", "FAILED"}),
            "total_count": len(rows),
            "thread_pool_utilization": self._thread_pool_utilization(rows),
            "status_counts": dict(state_counts),
            "threads": rows,
        }

    def _thread_pool_utilization(self, rows):
        active_workers = sum(1 for row in rows if row["thread_type"] == "WORKER" and row["status"] in {"RUNNING", "READY"})
        return {
            "active_workers": active_workers,
            "max_workers": 10,
            "utilization_percent": round((active_workers / 10) * 100, 2),
        }

    def get_native_threads(self):
        if psutil is None:
            return []
        process = psutil.Process(os.getpid())
        return process.threads()

    def _fetch_rows(self):
        if not self.db_path or not self.db_path.exists():
            return []

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, thread_id, thread_name, thread_type, status, created_at, cpu_time, memory_used, terminated_at
            FROM threads
            ORDER BY created_at DESC
            """
        ).fetchall()
        connection.close()

        result = []
        for row in rows:
            created_at = row["created_at"]
            terminated_at = row["terminated_at"]
            runtime_seconds = 0.0
            if created_at:
                try:
                    from datetime import datetime
                    created = datetime.fromisoformat(created_at)
                    ended = datetime.fromisoformat(terminated_at) if terminated_at else datetime.utcnow()
                    runtime_seconds = max(0.0, (ended - created).total_seconds())
                except ValueError:
                    runtime_seconds = 0.0

            result.append(
                {
                    "id": row["id"],
                    "thread_id": row["thread_id"],
                    "thread_name": row["thread_name"],
                    "thread_type": row["thread_type"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "cpu_time": round(row["cpu_time"] or 0.0, 4),
                    "memory_used": round(row["memory_used"] or 0.0, 4),
                    "terminated_at": row["terminated_at"],
                    "runtime_seconds": round(runtime_seconds, 2),
                }
            )
        return result
