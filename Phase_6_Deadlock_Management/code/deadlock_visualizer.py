from pathlib import Path

from .deadlock_detector import DeadlockDetector


class DeadlockVisualizer:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.detector = DeadlockDetector(self.output_dir)

    def current_view(self):
        return self.detector.detect_deadlock(record_event=False)
