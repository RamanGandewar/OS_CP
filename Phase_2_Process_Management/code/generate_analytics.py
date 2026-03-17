import sqlite3
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "Backend" / "database" / "crm.db"
ANALYTICS_DIR = ROOT_DIR / "Phase_2_Process_Management" / "analytics"


def fetch_process_rows():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT pid, state, cpu_time, created_at, terminated_at FROM processes")
    rows = cursor.fetchall()
    connection.close()
    return rows


def main():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    rows = fetch_process_rows()
    if not rows:
        print("No process rows found. Run the CRM and create some processes first.")
        return

    states = {}
    lifetimes = []
    cpu_times = []

    for _, state, cpu_time, created_at, terminated_at in rows:
        states[state] = states.get(state, 0) + 1
        cpu_times.append(cpu_time)
        if created_at and terminated_at:
            lifetime = max(0, datetime.fromisoformat(terminated_at) - datetime.fromisoformat(created_at))
            lifetimes.append(lifetime.total_seconds())

    plt.figure(figsize=(6, 6))
    plt.pie(states.values(), labels=states.keys(), autopct="%1.1f%%")
    plt.title("Process State Distribution")
    plt.savefig(ANALYTICS_DIR / "process_state_distribution_chart.png", bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.hist(cpu_times, bins=min(len(cpu_times), 8) or 1, color="#0d6efd", edgecolor="white")
    plt.title("CPU Time Distribution")
    plt.xlabel("CPU Time (seconds)")
    plt.ylabel("Processes")
    plt.savefig(ANALYTICS_DIR / "cpu_time_distribution_chart.png", bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(rows) + 1), list(range(1, len(rows) + 1)), marker="o", color="#fd7e14")
    plt.title("Process Creation Rate Over Time")
    plt.xlabel("Process Creation Sequence")
    plt.ylabel("Cumulative Processes")
    plt.savefig(ANALYTICS_DIR / "process_creation_rate_over_time.png", bbox_inches="tight")
    plt.close()

    if lifetimes:
        plt.figure(figsize=(8, 4))
        plt.plot(range(1, len(lifetimes) + 1), lifetimes, marker="o", color="#198754")
        plt.title("Average Process Lifetime Graph")
        plt.xlabel("Process Sample")
        plt.ylabel("Lifetime (seconds)")
        plt.savefig(ANALYTICS_DIR / "average_process_lifetime_graph.png", bbox_inches="tight")
        plt.close()

    print("Analytics charts generated in", ANALYTICS_DIR)


if __name__ == "__main__":
    main()
