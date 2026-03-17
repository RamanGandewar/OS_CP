from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class DiskVisualizer:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_movement_chart(self, result):
        figure, axis = plt.subplots(figsize=(8, 4))
        positions = list(range(len(result["path"])))
        axis.plot(positions, result["path"], marker="o", linewidth=2, color="#1f7a8c")
        axis.set_title(f'{result["algorithm"]} Disk Head Movement')
        axis.set_xlabel("Step")
        axis.set_ylabel("Track")
        axis.grid(True, alpha=0.25)
        output_path = self.output_dir / f'{result["algorithm"].lower().replace("-", "_")}_movement.png'
        figure.savefig(output_path, bbox_inches="tight")
        plt.close(figure)
        return output_path

    def save_comparison_chart(self, comparison):
        figure, axis = plt.subplots(figsize=(8, 4))
        labels = list(comparison.keys())
        values = [comparison[label]["total_seek"] for label in labels]
        axis.bar(labels, values, color=["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#8ecae6"])
        axis.set_title("Disk Scheduling Seek Time Comparison")
        axis.set_ylabel("Total Seek Time")
        output_path = self.output_dir / "seek_time_comparison.png"
        figure.savefig(output_path, bbox_inches="tight")
        plt.close(figure)
        return output_path
