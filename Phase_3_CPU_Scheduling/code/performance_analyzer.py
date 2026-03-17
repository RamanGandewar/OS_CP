class PerformanceAnalyzer:
    @staticmethod
    def calculate(tasks, total_elapsed):
        completed_tasks = [task for task in tasks if task.status == "COMPLETED"]
        if not completed_tasks:
            return {
                "average_waiting_time": 0,
                "average_turnaround_time": 0,
                "average_response_time": 0,
                "cpu_utilization": 0,
                "throughput": 0,
            }

        total_burst = sum(task.burst_time for task in completed_tasks)
        count = len(completed_tasks)
        safe_elapsed = total_elapsed if total_elapsed > 0 else 1

        return {
            "average_waiting_time": round(sum(task.waiting_time for task in completed_tasks) / count, 2),
            "average_turnaround_time": round(sum(task.turnaround_time for task in completed_tasks) / count, 2),
            "average_response_time": round(sum(task.response_time for task in completed_tasks) / count, 2),
            "cpu_utilization": round((total_burst / safe_elapsed) * 100, 2),
            "throughput": round(count / safe_elapsed, 4),
        }
