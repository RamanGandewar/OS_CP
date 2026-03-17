from collections import OrderedDict
from datetime import datetime


class PageTable:
    def __init__(self, fetch_page_callback, persist_callback, page_size=100, frame_count=5, algorithm="LRU"):
        self.fetch_page_callback = fetch_page_callback
        self.persist_callback = persist_callback
        self.page_size = page_size
        self.frame_count = frame_count
        self.algorithm = algorithm
        self.pages = {}
        self.frames = []
        self.fifo_queue = []
        self.lru_order = OrderedDict()
        self.page_faults = 0
        self.page_hits = 0
        self.history = []

    def reset(self):
        self.pages = {}
        self.frames = []
        self.fifo_queue = []
        self.lru_order = OrderedDict()
        self.page_faults = 0
        self.page_hits = 0
        self.history = []

    def get_page(self, page_number):
        timestamp = datetime.utcnow().isoformat()
        if page_number in self.pages:
            self.page_hits += 1
            self._mark_access(page_number)
            self.history.append({"page_number": page_number, "result": "hit", "timestamp": timestamp})
            self.persist_callback(page_number, in_memory=True, increment=True)
            return {"page_number": page_number, "records": self.pages[page_number], "hit": True, "evicted": None}

        self.page_faults += 1
        evicted = self._load_page(page_number)
        self.history.append({"page_number": page_number, "result": "fault", "timestamp": timestamp, "evicted": evicted})
        self.persist_callback(page_number, in_memory=True, increment=True)
        return {"page_number": page_number, "records": self.pages[page_number], "hit": False, "evicted": evicted}

    def get_record(self, record_number):
        page_number = record_number // self.page_size
        page = self.get_page(page_number)
        offset = record_number % self.page_size
        record = page["records"][offset] if offset < len(page["records"]) else None
        return page | {"record": record}

    def _load_page(self, page_number):
        evicted = None
        if len(self.frames) >= self.frame_count:
            evicted = self._evict_page()
            if evicted is not None:
                self.pages.pop(evicted, None)
                self.persist_callback(evicted, in_memory=False, increment=False)

        page_data = self.fetch_page_callback(page_number, self.page_size)
        self.pages[page_number] = page_data
        self.frames.append(page_number)
        self._mark_access(page_number, newly_loaded=True)
        return evicted

    def _evict_page(self):
        if self.algorithm == "FIFO":
            victim = self.fifo_queue.pop(0)
            self.frames.remove(victim)
            return victim

        victim = next(iter(self.lru_order.keys()))
        self.lru_order.pop(victim, None)
        self.frames.remove(victim)
        return victim

    def _mark_access(self, page_number, newly_loaded=False):
        if self.algorithm == "FIFO":
            if newly_loaded:
                self.fifo_queue.append(page_number)
            return

        self.lru_order.pop(page_number, None)
        self.lru_order[page_number] = datetime.utcnow().isoformat()

    def snapshot(self, total_records):
        total_accesses = self.page_hits + self.page_faults
        return {
            "page_size": self.page_size,
            "frame_count": self.frame_count,
            "algorithm": self.algorithm,
            "total_records": total_records,
            "loaded_pages": sorted(self.frames),
            "page_hits": self.page_hits,
            "page_faults": self.page_faults,
            "fault_rate": round((self.page_faults / total_accesses), 4) if total_accesses else 0,
            "history": self.history[-20:],
        }
