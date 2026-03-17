import random

from Phase_3_CPU_Scheduling.code.scheduler import CPUScheduler


def main():
    scheduler = CPUScheduler()
    scheduler.reset_tasks()

    for index in range(20):
        scheduler.add_task(
            task_type=random.choice(["REPORT", "EMAIL", "PDF", "NOTIFICATION"]),
            burst_time=random.randint(1, 4),
            priority=random.randint(1, 10),
            operation=f"validation-{index + 1}",
        )

    for algorithm in ("FCFS", "SJF", "PRIORITY", "RR"):
        scheduler.reset_tasks()
        if algorithm == "FCFS":
            result = scheduler.fcfs_schedule()
        elif algorithm == "SJF":
            result = scheduler.sjf_schedule()
        elif algorithm == "PRIORITY":
            result = scheduler.priority_schedule()
        else:
            result = scheduler.round_robin_schedule(time_quantum=2)
        print(algorithm, result["metrics"])

    print("Comparison", scheduler.compare_algorithms())


if __name__ == "__main__":
    main()
