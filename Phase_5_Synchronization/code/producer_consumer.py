from collections import deque
from datetime import datetime
import threading

from .mutex_manager import SYNC_MONITOR


class ProducerConsumerBuffer:
    def __init__(self, size=50):
        self.buffer = deque()
        self.size = size
        self.empty = threading.Semaphore(size)
        self.full = threading.Semaphore(0)
        self.mutex = threading.Lock()

    def produce(self, enquiry):
        if not self.empty.acquire(blocking=False):
            return {"success": False, "message": "Pending enquiry buffer is full"}
        with self.mutex:
            self.buffer.append(enquiry)
        self.full.release()
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Produced enquiry {enquiry}")
        return {"success": True, "buffer_size": len(self.buffer)}

    def consume(self):
        if not self.full.acquire(blocking=False):
            return {"success": False, "message": "No enquiries available for review"}
        with self.mutex:
            enquiry = self.buffer.popleft()
        self.empty.release()
        SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] Consumed enquiry {enquiry}")
        return {"success": True, "enquiry": enquiry, "buffer_size": len(self.buffer)}
