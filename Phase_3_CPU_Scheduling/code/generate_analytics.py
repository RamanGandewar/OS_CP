from pathlib import Path

import matplotlib.pyplot as plt
try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "Phase_3_CPU_Scheduling" / "output"
ANALYTICS_DIR = ROOT_DIR / "Phase_3_CPU_Scheduling" / "analytics"


def main():
    comparison_csv = OUTPUT_DIR / "performance_comparison.csv"
    if not comparison_csv.exists():
        print("performance_comparison.csv not found. Run scheduler comparisons first.")
        return
    if pd is None:
        print("pandas is required to generate Phase 3 analytics charts.")
        return

    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(comparison_csv, index_col=0)

    charts = [
        ("average_waiting_time", "Average Waiting Time", "average_waiting_time_graph.png"),
        ("average_turnaround_time", "Turnaround Time Comparison", "turnaround_time_comparison.png"),
        ("cpu_utilization", "CPU Utilization Chart", "cpu_utilization_chart.png"),
        ("throughput", "Throughput Analysis", "throughput_analysis.png"),
    ]

    for column, title, filename in charts:
        plt.figure(figsize=(8, 4))
        data[column].plot(kind="bar", color="#0d6efd")
        plt.title(title)
        plt.ylabel(column.replace("_", " ").title())
        plt.tight_layout()
        plt.savefig(ANALYTICS_DIR / filename, bbox_inches="tight")
        plt.close()

    print("Phase 3 analytics generated in", ANALYTICS_DIR)


if __name__ == "__main__":
    main()
