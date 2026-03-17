import csv
import sys
import time
import uuid
from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from queue import PriorityQueue, Queue

from flask import Flask
try:
    import pandas as pd
except ImportError:  # pragma: no cover - fallback while dependency installation catches up
    pd = None

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import TaskRecord, db
from .gantt_generator import GanttGenerator
from .performance_analyzer import PerformanceAnalyzer
from .task import Task

OUTPUT_DIR = ROOT_DIR / "Phase_3_CPU_Scheduling" / "output"
ANALYTICS_DIR = ROOT_DIR / "Phase_3_CPU_Scheduling" / "analytics"


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-3-cpu-scheduling-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class CPUScheduler:
    # Implements classic CPU scheduling policies for CRM background tasks.
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.analytics_dir = ANALYTICS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.output_dir / "task_execution.log"
        self.gantt_generator = GanttGenerator(self.output_dir)

    def add_task(self, task_type, burst_time, priority, requested_by=None, operation=None):
        app = _get_app()
        with app.app_context():
            task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
            record = TaskRecord(
                task_id=task_id,
                task_type=task_type,
                burst_time=burst_time,
                priority=priority,
                requested_by=requested_by,
                operation=operation,
                remaining_time=burst_time,
            )
            db.session.add(record)
            db.session.commit()
            self._append_log(f"[{datetime.utcnow().isoformat()}] Added task {task_id} ({task_type}) burst={burst_time}s priority={priority}")
            return record.to_dict()

    def add_real_world_task(self, task_name, requested_by=None):
        presets = {
            "monthly_sales_report": {"task_type": "REPORT", "burst_time": 10, "priority": 5, "operation": "monthly-sales-report"},
            "quotation_pdf": {"task_type": "PDF", "burst_time": 3, "priority": 1, "operation": "quotation-pdf"},
            "email_notification": {"task_type": "EMAIL", "burst_time": 2, "priority": 8, "operation": "email-notification"},
            "customer_export": {"task_type": "NOTIFICATION", "burst_time": 5, "priority": 4, "operation": "customer-export"},
        }
        config = presets[task_name]
        return self.add_task(requested_by=requested_by, **config)

    def get_queue(self):
        app = _get_app()
        with app.app_context():
            tasks = TaskRecord.query.order_by(TaskRecord.arrival_time.asc()).all()
            return [task.to_dict() for task in tasks]

    def reset_tasks(self):
        app = _get_app()
        with app.app_context():
            tasks = TaskRecord.query.all()
            for task in tasks:
                task.status = "PENDING"
                task.completion_time = None
                task.waiting_time = None
                task.turnaround_time = None
                task.response_time = None
                task.algorithm_used = None
                task.remaining_time = task.burst_time
            db.session.commit()

    def fcfs_schedule(self):
        return self._run_non_preemptive("FCFS", key_fn=lambda task: (task.arrival_time, task.task_id), use_queue=True)

    def sjf_schedule(self):
        return self._run_non_preemptive("SJF", key_fn=lambda task: (task.burst_time, task.arrival_time, task.task_id))

    def priority_schedule(self):
        return self._run_non_preemptive("PRIORITY", key_fn=lambda task: (task.priority, task.arrival_time, task.task_id))

    def round_robin_schedule(self, time_quantum=2):
        app = _get_app()
        with app.app_context():
            tasks = [Task.from_record(record, fresh=True) for record in TaskRecord.query.order_by(TaskRecord.arrival_time.asc()).all()]

        runnable = [deepcopy(task) for task in tasks]
        queue = deque(runnable)
        current_time = 0.0
        timeline = []
        first_response = {}

        while queue:
            task = queue.popleft()
            if task.remaining_time <= 0:
                continue

            if task.task_id not in first_response:
                first_response[task.task_id] = current_time

            execution_time = min(time_quantum, task.remaining_time)
            task.status = "RUNNING"
            timeline.append(
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "start": current_time,
                    "duration": execution_time,
                }
            )
            self._append_log(
                f"[{datetime.utcnow().isoformat()}] RR dispatch {task.task_id} for {execution_time}s (remaining before run: {task.remaining_time}s)"
            )
            time.sleep(execution_time)
            current_time += execution_time
            task.remaining_time -= execution_time

            if task.remaining_time > 0:
                task.status = "PENDING"
                queue.append(task)
            else:
                task.status = "COMPLETED"
                task.completion_time = task.arrival_time + timedelta(seconds=current_time)
                task.turnaround_time = current_time
                task.waiting_time = current_time - task.burst_time
                task.response_time = first_response[task.task_id]
                task.algorithm_used = "RR"

        completed_map = {task.task_id: task for task in runnable if task.status == "COMPLETED"}
        self._persist_results("RR", completed_map)
        metrics = PerformanceAnalyzer.calculate(list(completed_map.values()), current_time)
        chart_path = self.gantt_generator.generate("RR", timeline)
        return self._finalize_result("RR", list(completed_map.values()), timeline, metrics, chart_path)

    def compare_algorithms(self):
        snapshots = self._snapshot_tasks()
        comparisons = {}
        for algorithm in ("FCFS", "SJF", "PRIORITY", "RR"):
            tasks = [deepcopy(task) for task in snapshots]
            result = self._simulate_algorithm(tasks, algorithm)
            comparisons[algorithm] = result["metrics"]

        csv_path = self.output_dir / "performance_comparison.csv"
        if pd is not None:
            dataframe = pd.DataFrame.from_dict(comparisons, orient="index")
            dataframe.to_csv(csv_path)
        else:
            with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["algorithm", "average_waiting_time", "average_turnaround_time", "average_response_time", "cpu_utilization", "throughput"])
                for algorithm, metrics in comparisons.items():
                    writer.writerow(
                        [
                            algorithm,
                            metrics["average_waiting_time"],
                            metrics["average_turnaround_time"],
                            metrics["average_response_time"],
                            metrics["cpu_utilization"],
                            metrics["throughput"],
                        ]
                    )
        return {"comparisons": comparisons, "csv_path": str(csv_path)}

    def get_performance_metrics(self):
        return self.compare_algorithms()

    def _run_non_preemptive(self, algorithm_name, key_fn, use_queue=False):
        app = _get_app()
        with app.app_context():
            tasks = [Task.from_record(record, fresh=True) for record in TaskRecord.query.order_by(TaskRecord.arrival_time.asc()).all()]

        runnable = [deepcopy(task) for task in tasks]
        ordered = sorted(runnable, key=key_fn)
        current_time = 0.0
        timeline = []

        if use_queue:
            queue = Queue()
            for task in ordered:
                queue.put(task)
            ordered = []
            while not queue.empty():
                ordered.append(queue.get())

        for task in ordered:
            task.status = "RUNNING"
            task.waiting_time = current_time
            task.response_time = current_time
            timeline.append(
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "start": current_time,
                    "duration": task.burst_time,
                }
            )
            self._append_log(f"[{datetime.utcnow().isoformat()}] {algorithm_name} dispatch {task.task_id} for {task.burst_time}s")
            time.sleep(task.burst_time)
            current_time += task.burst_time
            task.completion_time = task.arrival_time + timedelta(seconds=current_time)
            task.turnaround_time = current_time
            task.status = "COMPLETED"
            task.algorithm_used = algorithm_name
            task.remaining_time = 0

        completed_map = {task.task_id: task for task in ordered}
        self._persist_results(algorithm_name, completed_map)
        metrics = PerformanceAnalyzer.calculate(ordered, current_time)
        chart_path = self.gantt_generator.generate(algorithm_name, timeline)
        return self._finalize_result(algorithm_name, ordered, timeline, metrics, chart_path)

    def _persist_results(self, algorithm_name, completed_map):
        app = _get_app()
        with app.app_context():
            records = TaskRecord.query.all()
            for record in records:
                task = completed_map.get(record.task_id)
                if task:
                    record.status = task.status
                    record.completion_time = task.completion_time
                    record.waiting_time = task.waiting_time
                    record.turnaround_time = task.turnaround_time
                    record.response_time = task.response_time
                    record.algorithm_used = algorithm_name
                    record.remaining_time = task.remaining_time
            db.session.commit()

    def _finalize_result(self, algorithm_name, tasks, timeline, metrics, chart_path):
        return {
            "algorithm": algorithm_name,
            "tasks": [task.to_dict() for task in tasks],
            "timeline": timeline,
            "metrics": metrics,
            "chart_path": str(chart_path) if chart_path else None,
        }

    def _simulate_algorithm(self, tasks, algorithm_name):
        if algorithm_name == "FCFS":
            ordered = sorted(tasks, key=lambda task: (task.arrival_time, task.task_id))
            return self._simulate_non_preemptive(ordered, "FCFS")
        if algorithm_name == "SJF":
            ordered = sorted(tasks, key=lambda task: (task.burst_time, task.arrival_time, task.task_id))
            return self._simulate_non_preemptive(ordered, "SJF")
        if algorithm_name == "PRIORITY":
            priority_queue = PriorityQueue()
            for task in tasks:
                priority_queue.put((task.priority, task.arrival_time, task.task_id, task))
            ordered = []
            while not priority_queue.empty():
                ordered.append(priority_queue.get()[3])
            return self._simulate_non_preemptive(ordered, "PRIORITY")
        return self._simulate_round_robin(tasks, 2)

    def _simulate_non_preemptive(self, ordered, algorithm_name):
        current_time = 0.0
        timeline = []
        for task in ordered:
            task.waiting_time = current_time
            task.response_time = current_time
            timeline.append({"task_id": task.task_id, "task_type": task.task_type, "start": current_time, "duration": task.burst_time})
            current_time += task.burst_time
            task.turnaround_time = current_time
            task.status = "COMPLETED"
            task.algorithm_used = algorithm_name
            task.remaining_time = 0
        return {"metrics": PerformanceAnalyzer.calculate(ordered, current_time), "timeline": timeline}

    def _simulate_round_robin(self, tasks, time_quantum):
        queue = deque(tasks)
        current_time = 0.0
        first_response = {}
        while queue:
            task = queue.popleft()
            if task.remaining_time <= 0:
                continue
            if task.task_id not in first_response:
                first_response[task.task_id] = current_time
            execution = min(task.remaining_time, time_quantum)
            current_time += execution
            task.remaining_time -= execution
            if task.remaining_time > 0:
                queue.append(task)
            else:
                task.waiting_time = current_time - task.burst_time
                task.turnaround_time = current_time
                task.response_time = first_response[task.task_id]
                task.status = "COMPLETED"
                task.algorithm_used = "RR"
        return {"metrics": PerformanceAnalyzer.calculate(tasks, current_time), "timeline": []}

    def _snapshot_tasks(self):
        app = _get_app()
        with app.app_context():
            records = TaskRecord.query.order_by(TaskRecord.arrival_time.asc()).all()
            return [Task.from_record(record, fresh=True) for record in records]

    def _append_log(self, message):
        existing = self.log_path.read_text(encoding="utf-8") if self.log_path.exists() else ""
        self.log_path.write_text(existing + message + "\n", encoding="utf-8")
