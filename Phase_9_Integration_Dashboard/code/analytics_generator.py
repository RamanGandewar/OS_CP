from pathlib import Path

from Backend.models import CacheStat, DeadlockEvent, DiskRequest, ProcessRecord, TaskRecord


class AnalyticsGenerator:
    def __init__(self, analytics_dir):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

    def summary(self):
        latest_cache = CacheStat.query.order_by(CacheStat.id.desc()).first()
        return {
            "processes_created": ProcessRecord.query.count(),
            "tasks_executed": TaskRecord.query.filter_by(status="COMPLETED").count(),
            "deadlocks_detected": DeadlockEvent.query.count(),
            "disk_requests": DiskRequest.query.count(),
            "latest_cache_hit_ratio": latest_cache.hit_ratio if latest_cache else 0,
        }

    def generate_files(self):
        summary = self.summary()
        report_path = self.analytics_dir / "overall_system_performance_report.md"
        report_path.write_text(
            "\n".join(
                [
                    "# Overall System Performance Report",
                    "",
                    f"- Total processes created: {summary['processes_created']}",
                    f"- Completed tasks: {summary['tasks_executed']}",
                    f"- Deadlocks detected: {summary['deadlocks_detected']}",
                    f"- Disk requests observed: {summary['disk_requests']}",
                    f"- Latest cache hit ratio: {summary['latest_cache_hit_ratio']:.2f}",
                ]
            ),
            encoding="utf-8",
        )
        recommendations = self.analytics_dir / "optimization_recommendations.md"
        recommendations.write_text(
            "\n".join(
                [
                    "# Optimization Recommendations",
                    "",
                    "- Prefer low-seek disk scheduling strategies like SSTF or LOOK when request locality is high.",
                    "- Increase memory frames if page faults remain higher than page hits under report workloads.",
                    "- Review lock contention hotspots whenever the synchronization wait queue grows persistently.",
                    "- Use the unified dashboard alerts panel as the first checkpoint during live demos.",
                ]
            ),
            encoding="utf-8",
        )
        return {"performance_report": str(report_path), "recommendations": str(recommendations)}

