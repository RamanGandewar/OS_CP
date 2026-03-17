from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class Task:
    # Models a schedulable CPU-bound CRM task.
    task_id: str
    task_type: str
    burst_time: int
    priority: int
    arrival_time: datetime
    completion_time: datetime | None = None
    waiting_time: float = 0.0
    turnaround_time: float = 0.0
    response_time: float = 0.0
    status: str = "PENDING"
    algorithm_used: str | None = None
    remaining_time: int | None = None
    operation: str | None = None

    def __post_init__(self):
        if self.remaining_time is None:
            self.remaining_time = self.burst_time

    @classmethod
    def from_record(cls, record, fresh=False):
        return cls(
            task_id=record.task_id,
            task_type=record.task_type,
            burst_time=record.burst_time,
            priority=record.priority,
            arrival_time=record.arrival_time,
            completion_time=None if fresh else record.completion_time,
            waiting_time=0.0 if fresh else (record.waiting_time or 0.0),
            turnaround_time=0.0 if fresh else (record.turnaround_time or 0.0),
            response_time=0.0 if fresh else (record.response_time or 0.0),
            status="PENDING" if fresh else record.status,
            algorithm_used=None if fresh else record.algorithm_used,
            remaining_time=record.burst_time if fresh else record.remaining_time,
            operation=record.operation,
        )

    def to_dict(self):
        payload = asdict(self)
        payload["arrival_time"] = self.arrival_time.isoformat() if self.arrival_time else None
        payload["completion_time"] = self.completion_time.isoformat() if self.completion_time else None
        return payload
