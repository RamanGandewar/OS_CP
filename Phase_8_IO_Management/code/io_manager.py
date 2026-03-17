from pathlib import Path

from Backend.models import DiskRequest, db

from .disk_scheduler import DiskScheduler
from .disk_visualizer import DiskVisualizer
from .io_buffer import IOBufferPool
from .spooling_manager import SpoolingManager


class IOManager:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scheduler = DiskScheduler(current_head=50, max_track=100)
        self.buffer_pool = IOBufferPool(buffer_count=4, buffer_size=256)
        self.spooler = SpoolingManager()
        self.default_requests = [
            {"request_type": "Save Quotation PDF", "track_number": 45},
            {"request_type": "Load Customer Data", "track_number": 12},
            {"request_type": "Generate Report", "track_number": 78},
            {"request_type": "Save Invoice", "track_number": 23},
            {"request_type": "Export Excel", "track_number": 67},
        ]
        self.reference_sequence = [45, 12, 78, 23, 67, 89, 34, 56]
        self.visualizer = DiskVisualizer(self.output_dir)
        self.last_comparison = {}
        self.initialized = False

    def ensure_seed_requests(self):
        if self.initialized:
            return
        if DiskRequest.query.count() == 0:
            for item in self.default_requests:
                db.session.add(DiskRequest(request_type=item["request_type"], track_number=item["track_number"]))
            db.session.commit()
        self.compare_algorithms()
        self.initialized = True

    def add_request(self, request_type, track_number):
        request_record = DiskRequest(request_type=request_type, track_number=int(track_number))
        db.session.add(request_record)
        db.session.commit()
        self.reference_sequence.append(int(track_number))
        self.compare_algorithms()
        return request_record.to_dict()

    def compare_algorithms(self, requests=None, current_head=50):
        sequence = [int(track) for track in (requests or self.reference_sequence)]
        self.scheduler.current_head = int(current_head)
        comparison = self.scheduler.compare_all(sequence)
        for algorithm, result in comparison.items():
            self.visualizer.save_movement_chart(result)
        best_algorithm = min(comparison.items(), key=lambda item: item[1]["total_seek"])[0] if comparison else None
        if best_algorithm:
            for track in sequence:
                DiskRequest.query.filter_by(track_number=track).update({"algorithm_used": best_algorithm})
        self.visualizer.save_comparison_chart(comparison)
        db.session.commit()
        self.last_comparison = comparison
        return comparison

    def allocate_buffer(self, request_type, size):
        return self.buffer_pool.allocate(request_type, int(size))

    def release_buffer(self, buffer_id):
        return self.buffer_pool.release(int(buffer_id))

    def enqueue_print(self, job_type, filename, pages, user_id=None):
        return self.spooler.enqueue(job_type, filename, int(pages), user_id)

    def process_print(self):
        return self.spooler.process_next()

    def chart_path(self, algorithm):
        if algorithm == "comparison":
            return self.output_dir / "seek_time_comparison.png"
        return self.output_dir / f"{algorithm.lower().replace('-', '_')}_movement.png"

    def get_monitor_payload(self):
        requests = [item.to_dict() for item in DiskRequest.query.order_by(DiskRequest.arrival_time.asc()).all()]
        comparison = self.last_comparison or self.compare_algorithms()
        best_algorithm = min(comparison.items(), key=lambda item: item[1]["total_seek"])[0] if comparison else None
        return {
            "current_head": self.scheduler.current_head,
            "max_track": self.scheduler.max_track,
            "requests": requests,
            "reference_sequence": self.reference_sequence,
            "comparison": comparison,
            "best_algorithm": best_algorithm,
            "buffer_pool": self.buffer_pool.snapshot(),
            "print_queue": self.spooler.snapshot(),
            "chart_urls": {
                "comparison": "/api/io/charts/comparison",
                "fcfs": "/api/io/charts/fcfs",
                "sstf": "/api/io/charts/sstf",
                "scan": "/api/io/charts/scan",
                "c-scan": "/api/io/charts/c-scan",
                "look": "/api/io/charts/look",
                "c-look": "/api/io/charts/c-look",
            },
        }
