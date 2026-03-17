import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "Backend" / "database" / "crm.db"
ANALYTICS_DIR = ROOT_DIR / "Phase_4_Thread_Management" / "analytics"


def main():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    rows = connection.execute("SELECT status, cpu_time, memory_used FROM threads").fetchall()
    connection.close()

    if not rows:
        print("No thread data found. Run the CRM and create thread activity first.")
        return

    statuses = {}
    cpu_usage = []
    memory_usage = []
    for status, cpu_time, memory_used in rows:
        statuses[status] = statuses.get(status, 0) + 1
        cpu_usage.append(cpu_time)
        memory_usage.append(memory_used)

    plt.figure(figsize=(8, 4))
    plt.bar(statuses.keys(), statuses.values(), color="#0d6efd")
    plt.title("Thread Count Over Time")
    plt.tight_layout()
    plt.savefig(ANALYTICS_DIR / "thread_count_over_time_graph.png", bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.hist(cpu_usage, bins=min(len(cpu_usage), 8) or 1, color="#198754", edgecolor="white")
    plt.title("Thread CPU Usage Distribution")
    plt.tight_layout()
    plt.savefig(ANALYTICS_DIR / "thread_cpu_usage_distribution.png", bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.hist(memory_usage, bins=min(len(memory_usage), 8) or 1, color="#fd7e14", edgecolor="white")
    plt.title("Thread Memory Usage Distribution")
    plt.tight_layout()
    plt.savefig(ANALYTICS_DIR / "thread_pool_efficiency_metrics.png", bbox_inches="tight")
    plt.close()

    print("Phase 4 analytics generated in", ANALYTICS_DIR)


if __name__ == "__main__":
    main()
