import multiprocessing
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import ProcessLog, ProcessRecord, db
from .process_monitor import ProcessMonitor

PHASE_2_OUTPUT_DIR = ROOT_DIR / "Phase_2_Process_Management" / "output"
PROCESS_MONITOR = ProcessMonitor(PHASE_2_OUTPUT_DIR)
PROCESS_REGISTRY = {}
SPAWN_CONTEXT = multiprocessing.get_context("spawn")
VALID_TRANSITIONS = {
    "NEW": {"READY", "TERMINATED"},
    "READY": {"RUNNING", "TERMINATED"},
    "RUNNING": {"WAITING", "TERMINATED"},
    "WAITING": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-2-process-management-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


def transition_process_state(pid, new_state, message):
    app = _get_app()
    with app.app_context():
        record = ProcessRecord.query.filter_by(pid=pid).first()
        if not record:
            return

        previous_state = record.state
        if previous_state != new_state and new_state not in VALID_TRANSITIONS.get(previous_state, set()):
            message = f"{message} (forced transition)"

        record.state = new_state
        if new_state == "TERMINATED":
            record.terminated_at = datetime.utcnow()

        db.session.add(
            ProcessLog(
                pid=pid,
                previous_state=previous_state,
                new_state=new_state,
                message=message,
            )
        )
        db.session.commit()

    timestamp = datetime.utcnow().isoformat()
    PROCESS_MONITOR.append_transition_log(f"[{timestamp}] PID {pid}: {previous_state} -> {new_state} | {message}")


def update_cpu_time(pid, cpu_time):
    app = _get_app()
    with app.app_context():
        record = ProcessRecord.query.filter_by(pid=pid).first()
        if not record:
            return
        record.cpu_time = cpu_time
        db.session.commit()


def register_process(pid, user_id, parent_pid, priority, task_type, operation):
    app = _get_app()
    with app.app_context():
        record = ProcessRecord(
            pid=pid,
            user_id=user_id,
            state="NEW",
            priority=priority,
            cpu_time=0.0,
            parent_pid=parent_pid,
            task_type=task_type,
            operation=operation,
        )
        db.session.add(record)
        db.session.add(
            ProcessLog(
                pid=pid,
                previous_state=None,
                new_state="NEW",
                message=f"{task_type} process created",
            )
        )
        db.session.commit()

    timestamp = datetime.utcnow().isoformat()
    PROCESS_MONITOR.append_creation_log(
        f"[{timestamp}] PID {pid} created for user {user_id or 'system'} as {task_type} ({operation or 'n/a'})"
    )
    transition_process_state(pid, "READY", "Process added to ready queue")


def terminate_process_record(pid, reason):
    transition_process_state(pid, "TERMINATED", reason)


def _session_worker(stop_event, bootstrap_event):
    process = multiprocessing.current_process()
    pid = process.pid
    bootstrap_event.wait()
    start = time.perf_counter()
    transition_process_state(pid, "RUNNING", f"Session process {process.name} started")
    waiting_logged = False

    try:
        while not stop_event.is_set():
            elapsed = time.perf_counter() - start
            update_cpu_time(pid, elapsed)
            if not waiting_logged:
                transition_process_state(pid, "WAITING", "Session is idle and waiting for CRM events")
                waiting_logged = True
            time.sleep(1)
            if not stop_event.is_set():
                transition_process_state(pid, "RUNNING", "Session resumed handling user context")
                waiting_logged = False
    finally:
        update_cpu_time(pid, time.perf_counter() - start)
        terminate_process_record(pid, "Session process exited gracefully")


def _background_worker(task_type, duration, payload, bootstrap_event):
    pid = multiprocessing.current_process().pid
    bootstrap_event.wait()
    start = time.perf_counter()
    transition_process_state(pid, "RUNNING", f"{task_type} process executing exec() workload")
    time.sleep(max(duration, 1))
    update_cpu_time(pid, time.perf_counter() - start)
    transition_process_state(pid, "WAITING", f"{task_type} process reached wait() barrier")
    time.sleep(0.5)
    terminate_process_record(pid, f"{task_type} process completed payload: {payload}")


def create_session_process(user_id, priority=5):
    stop_event = SPAWN_CONTEXT.Event()
    bootstrap_event = SPAWN_CONTEXT.Event()
    process = SPAWN_CONTEXT.Process(target=_session_worker, args=(stop_event, bootstrap_event), daemon=True)
    process.start()
    pid = process.pid
    register_process(pid, user_id, os.getpid(), priority, "session", "user-login")
    bootstrap_event.set()
    PROCESS_REGISTRY[pid] = {"process": process, "stop_event": stop_event}
    return pid


def create_background_process(user_id, task_type, operation, priority=5, duration=2, payload=None):
    bootstrap_event = SPAWN_CONTEXT.Event()
    process = SPAWN_CONTEXT.Process(
        target=_background_worker,
        args=(task_type, duration, payload or {}, bootstrap_event),
        daemon=True,
    )
    process.start()
    pid = process.pid
    register_process(pid, user_id, os.getpid(), priority, task_type, operation)
    bootstrap_event.set()
    PROCESS_REGISTRY[pid] = {"process": process, "stop_event": None}
    return pid


def terminate_session_process(pid):
    process_info = PROCESS_REGISTRY.get(pid)
    if not process_info:
        terminate_process_record(pid, "Session cleanup requested for non-registered process")
        return

    stop_event = process_info["stop_event"]
    process = process_info["process"]
    if stop_event:
        stop_event.set()
    process.join(timeout=5)
    if process.is_alive():
        process.terminate()
        process.join(timeout=2)
        terminate_process_record(pid, "Forced termination after exit() timeout")
    PROCESS_REGISTRY.pop(pid, None)


def wait_for_background_process(pid, timeout=10):
    process_info = PROCESS_REGISTRY.get(pid)
    if not process_info:
        return False
    process = process_info["process"]
    process.join(timeout=timeout)
    finished = not process.is_alive()
    if finished:
        PROCESS_REGISTRY.pop(pid, None)
    return finished


def cleanup_dead_processes():
    for pid, process_info in list(PROCESS_REGISTRY.items()):
        process = process_info["process"]
        if not process.is_alive():
            PROCESS_REGISTRY.pop(pid, None)
            terminate_process_record(pid, "Cleanup thread marked orphaned process as terminated")


def get_monitor_payload():
    cleanup_dead_processes()
    return PROCESS_MONITOR.get_process_summary()


def get_process_logs(limit=100):
    return PROCESS_MONITOR.get_recent_logs(limit=limit)
