from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class PCB:
    # A simplified process control block used to expose OS concepts in the CRM.
    pid: int
    state: str
    priority: int
    cpu_time: float
    created_at: str
    parent_pid: int | None
    user_id: int | None
    task_type: str
    operation: str | None = None

    @classmethod
    def from_process_record(cls, record):
        return cls(
            pid=record.pid,
            state=record.state,
            priority=record.priority,
            cpu_time=record.cpu_time,
            created_at=record.created_at.isoformat() if record.created_at else datetime.utcnow().isoformat(),
            parent_pid=record.parent_pid,
            user_id=record.user_id,
            task_type=record.task_type,
            operation=record.operation,
        )

    def to_dict(self):
        return asdict(self)
