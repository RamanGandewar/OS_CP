import threading


class RaceConditionDemo:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def run_unsynchronized(self, iterations=1000):
        self.value = 0

        def worker():
            for _ in range(iterations):
                current = self.value
                current += 1
                self.value = current

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return {"mode": "UNSYNCHRONIZED", "expected": iterations * 2, "actual": self.value}

    def run_synchronized(self, iterations=1000):
        self.value = 0

        def worker():
            for _ in range(iterations):
                with self.lock:
                    self.value += 1

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return {"mode": "SYNCHRONIZED", "expected": iterations * 2, "actual": self.value}
