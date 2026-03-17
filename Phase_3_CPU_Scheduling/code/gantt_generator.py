from pathlib import Path

import matplotlib.pyplot as plt


TASK_COLORS = {
    "REPORT": "#0d6efd",
    "EMAIL": "#198754",
    "PDF": "#fd7e14",
    "NOTIFICATION": "#6f42c1",
}


class GanttGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, algorithm_name, timeline):
        if not timeline:
            return None

        figure, axis = plt.subplots(figsize=(12, 4))
        yticks = []
        ylabels = []

        for index, segment in enumerate(timeline):
            start = segment["start"]
            duration = segment["duration"]
            task_id = segment["task_id"]
            task_type = segment["task_type"]
            axis.broken_barh(
                [(start, duration)],
                (index * 10, 8),
                facecolors=TASK_COLORS.get(task_type, "#6c757d"),
            )
            axis.text(start + (duration / 2), (index * 10) + 4, task_id, ha="center", va="center", color="white")
            yticks.append((index * 10) + 4)
            ylabels.append(task_id)

        axis.set_xlabel("Time (seconds)")
        axis.set_ylabel("Tasks")
        axis.set_title(f"{algorithm_name} Gantt Chart")
        axis.set_yticks(yticks)
        axis.set_yticklabels(ylabels)
        axis.grid(True, axis="x", linestyle="--", alpha=0.4)
        figure.tight_layout()

        output_path = self.output_dir / f"{algorithm_name.lower()}_gantt_chart.png"
        figure.savefig(output_path, bbox_inches="tight")
        plt.close(figure)
        return output_path
