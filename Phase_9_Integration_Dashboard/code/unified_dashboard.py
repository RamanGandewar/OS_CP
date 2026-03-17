from datetime import datetime

from Backend.models import (
    CacheStat,
    Customer,
    DeadlockEvent,
    DiskRequest,
    Enquiry,
    Invoice,
    LockQueueEntry,
    LockRecord,
    MemoryPage,
    PrintQueueJob,
    ProcessLog,
    ProcessRecord,
    Quotation,
    SalesOrder,
    TaskRecord,
    ThreadRecord,
)
from Phase_2_Process_Management.code.process_manager import get_monitor_payload as get_process_payload, get_process_logs
from Phase_3_CPU_Scheduling.code.routes.scheduler_routes import scheduler
from Phase_4_Thread_Management.code.thread_manager import thread_manager
from Phase_5_Synchronization.code.mutex_manager import SYNC_MONITOR
from Phase_6_Deadlock_Management.code.routes.deadlock_routes import resource_manager, visualizer
from Phase_7_Memory_Management.code.routes.memory_routes import memory_monitor
from Phase_8_IO_Management.code.routes.io_routes import io_manager


class UnifiedDashboard:
    def __init__(self, analytics_generator, performance_report):
        self.analytics_generator = analytics_generator
        self.performance_report = performance_report
        self.started_at = datetime.utcnow()

    def snapshot(self):
        io_manager.ensure_seed_requests()
        process_payload = get_process_payload()
        scheduler_queue = scheduler.get_queue()
        scheduler_compare = scheduler.compare_algorithms()
        thread_payload = thread_manager.get_monitor_payload()
        sync_payload = SYNC_MONITOR.get_monitor_payload()
        deadlock_state = resource_manager.get_state()
        deadlock_state["visualization"] = visualizer.current_view()
        deadlock_state["events"] = [event.to_dict() for event in DeadlockEvent.query.order_by(DeadlockEvent.id.desc()).limit(20).all()]
        memory_payload = memory_monitor.get_monitor_payload()
        io_payload = io_manager.get_monitor_payload()

        overview = {
            "uptime_seconds": round((datetime.utcnow() - self.started_at).total_seconds(), 2),
            "active_processes": process_payload.get("active_count", 0),
            "task_queue_size": len([task for task in scheduler_queue if task["status"] != "COMPLETED"]),
            "thread_count": thread_payload.get("active_count", 0),
            "resource_utilization": {
                "active_locks": len(sync_payload.get("active_locks", [])),
                "deadlock_resources": len(deadlock_state.get("resources", [])),
            },
            "memory_usage": {
                "loaded_pages": len(memory_payload.get("page_table", {}).get("loaded_pages", [])),
                "page_faults": memory_payload.get("page_table", {}).get("page_faults", 0),
                "cache_hit_ratio": memory_payload.get("cache", {}).get("customer", {}).get("hit_ratio", 0),
            },
            "io_queue_size": len(io_payload.get("requests", [])),
            "crm_counts": {
                "customers": Customer.query.count(),
                "enquiries": Enquiry.query.count(),
                "quotations": Quotation.query.count(),
                "orders": SalesOrder.query.count(),
                "invoices": Invoice.query.count(),
            },
        }

        alerts = []
        if deadlock_state.get("visualization", {}).get("deadlock"):
            alerts.append({"type": "danger", "message": "Deadlock detected in the resource allocation graph."})
        if sync_payload.get("lock_queue"):
            alerts.append({"type": "warning", "message": "Synchronization wait queue has pending lock requests."})
        if memory_payload.get("page_table", {}).get("page_faults", 0) > memory_payload.get("page_table", {}).get("page_hits", 0):
            alerts.append({"type": "info", "message": "Paging workload is currently fault-heavy; consider reviewing frame count."})

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": overview,
            "alerts": alerts,
            "processes": process_payload | {"logs": get_process_logs(limit=100)},
            "scheduler": {
                "queue": scheduler_queue,
                "comparison": scheduler_compare,
            },
            "threads": thread_payload,
            "synchronization": sync_payload,
            "deadlock": deadlock_state,
            "memory": memory_payload,
            "io": io_payload,
            "analytics": self.analytics_generator.summary(),
            "performance_report": self.performance_report.summary(),
        }

