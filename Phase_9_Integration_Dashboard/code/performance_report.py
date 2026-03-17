from pathlib import Path

from Backend.models import CacheStat, DeadlockEvent, DiskRequest, MemoryPage, ProcessRecord, TaskRecord, ThreadRecord


class PerformanceReport:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def summary(self):
        completed_tasks = TaskRecord.query.filter_by(status="COMPLETED").count()
        latest_cache = CacheStat.query.order_by(CacheStat.id.desc()).first()
        return {
            "total_processes_created": ProcessRecord.query.count(),
            "total_tasks_executed": completed_tasks,
            "total_threads_tracked": ThreadRecord.query.count(),
            "synchronization_conflicts": DeadlockEvent.query.count(),
            "page_fault_rate": self._page_fault_rate(),
            "cache_efficiency": latest_cache.hit_ratio if latest_cache else 0,
            "disk_io_throughput": DiskRequest.query.count(),
        }

    def generate_markdown(self):
        summary = self.summary()
        output_path = self.output_dir / "system_performance_report.md"
        output_path.write_text(
            "\n".join(
                [
                    "# System Performance Report",
                    "",
                    f"- Total processes created: {summary['total_processes_created']}",
                    f"- Total tasks executed: {summary['total_tasks_executed']}",
                    f"- Total threads tracked: {summary['total_threads_tracked']}",
                    f"- Deadlocks detected/resolved entries: {summary['synchronization_conflicts']}",
                    f"- Page fault rate: {summary['page_fault_rate']:.2f}",
                    f"- Cache efficiency: {summary['cache_efficiency']:.2f}",
                    f"- Disk I/O throughput indicator: {summary['disk_io_throughput']}",
                ]
            ),
            encoding="utf-8",
        )
        return output_path

    def _page_fault_rate(self):
        total_page_accesses = sum(page.access_count or 0 for page in MemoryPage.query.all())
        if total_page_accesses == 0:
            return 0.0
        fault_pages = MemoryPage.query.filter_by(in_memory=True).count()
        return fault_pages / total_page_accesses

