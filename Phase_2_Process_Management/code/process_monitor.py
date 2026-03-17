from collections import Counter
import os
from pathlib import Path

try:
    import psutil
except ImportError:  # pragma: no cover - fallback for environments pending dependency install
    psutil = None

from Backend.models import ProcessLog, ProcessRecord
from .pcb import PCB


class ProcessMonitor:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.creation_log_path = self.output_dir / "process_creation.log"
        self.transition_log_path = self.output_dir / "process_state_transitions.log"

    def append_creation_log(self, message):
        self.creation_log_path.write_text(
            self._append_line(self.creation_log_path, message),
            encoding="utf-8",
        )

    def append_transition_log(self, message):
        self.transition_log_path.write_text(
            self._append_line(self.transition_log_path, message),
            encoding="utf-8",
        )

    def _append_line(self, path, message):
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        return existing + message + "\n"

    def get_process_summary(self):
        processes = ProcessRecord.query.order_by(ProcessRecord.created_at.desc()).all()
        state_counts = Counter(item.state for item in processes)
        active = 0
        for process in processes:
            if process.state != "TERMINATED" and self._pid_exists(process.pid):
                active += 1
        return {
            "active_count": active,
            "total_count": len(processes),
            "state_counts": dict(state_counts),
            "processes": [PCB.from_process_record(item).to_dict() | {"username": item.user.username if item.user else "system"} for item in processes],
        }

    def get_recent_logs(self, limit=100):
        logs = ProcessLog.query.order_by(ProcessLog.logged_at.desc()).limit(limit).all()
        return [item.to_dict() for item in logs]

    def _pid_exists(self, pid):
        if psutil is not None:
            return psutil.pid_exists(pid)
        try:
            os.kill(pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True
