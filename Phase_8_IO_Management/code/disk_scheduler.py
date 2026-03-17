class DiskScheduler:
    def __init__(self, current_head=50, max_track=100):
        self.current_head = current_head
        self.max_track = max_track

    def _build_result(self, algorithm, path):
        total_seek = 0
        steps = []
        for start, end in zip(path, path[1:]):
            distance = abs(end - start)
            total_seek += distance
            steps.append({"from": start, "to": end, "distance": distance})
        return {"algorithm": algorithm, "path": path, "steps": steps, "total_seek": total_seek}

    def fcfs(self, requests):
        path = [self.current_head] + list(requests)
        return self._build_result("FCFS", path)

    def sstf(self, requests):
        current = self.current_head
        remaining = list(requests)
        path = [current]
        while remaining:
            closest = min(remaining, key=lambda track: abs(track - current))
            path.append(closest)
            current = closest
            remaining.remove(closest)
        return self._build_result("SSTF", path)

    def scan(self, requests, direction="up"):
        current = self.current_head
        lower = sorted([track for track in requests if track < current])
        upper = sorted([track for track in requests if track >= current])
        path = [current]
        if direction == "up":
            path.extend(upper)
            if upper and upper[-1] != self.max_track:
                path.append(self.max_track)
            path.extend(reversed(lower))
        else:
            path.extend(reversed(lower))
            if lower and lower[0] != 0:
                path.append(0)
            path.extend(upper)
        return self._build_result("SCAN", path)

    def cscan(self, requests):
        current = self.current_head
        lower = sorted([track for track in requests if track < current])
        upper = sorted([track for track in requests if track >= current])
        path = [current]
        path.extend(upper)
        if upper and upper[-1] != self.max_track:
            path.append(self.max_track)
        if lower:
            path.append(0)
            path.extend(lower)
        return self._build_result("C-SCAN", path)

    def look(self, requests, direction="up"):
        current = self.current_head
        lower = sorted([track for track in requests if track < current])
        upper = sorted([track for track in requests if track >= current])
        path = [current]
        if direction == "up":
            path.extend(upper)
            path.extend(reversed(lower))
        else:
            path.extend(reversed(lower))
            path.extend(upper)
        return self._build_result("LOOK", path)

    def clook(self, requests):
        current = self.current_head
        lower = sorted([track for track in requests if track < current])
        upper = sorted([track for track in requests if track >= current])
        path = [current]
        path.extend(upper)
        if lower:
            path.append(lower[0])
            path.extend(lower[1:])
        return self._build_result("C-LOOK", path)

    def compare_all(self, requests):
        return {
            "FCFS": self.fcfs(requests),
            "SSTF": self.sstf(requests),
            "SCAN": self.scan(requests),
            "C-SCAN": self.cscan(requests),
            "LOOK": self.look(requests),
            "C-LOOK": self.clook(requests),
        }
