from collections import OrderedDict, deque


class PageReplacement:
    def __init__(self, frame_count=5):
        self.frame_count = frame_count

    def fifo_faults(self, reference_string):
        frames = deque()
        loaded = set()
        faults = 0
        timeline = []

        for page in reference_string:
            hit = page in loaded
            if not hit:
                faults += 1
                if len(frames) >= self.frame_count:
                    evicted = frames.popleft()
                    loaded.remove(evicted)
                frames.append(page)
                loaded.add(page)
            timeline.append({"page": page, "frames": list(frames), "hit": hit})

        return {"algorithm": "FIFO", "page_faults": faults, "timeline": timeline, "frames": list(frames)}

    def lru_faults(self, reference_string):
        frames = OrderedDict()
        faults = 0
        timeline = []

        for page in reference_string:
            hit = page in frames
            if hit:
                frames.move_to_end(page)
            else:
                faults += 1
                if len(frames) >= self.frame_count:
                    frames.popitem(last=False)
                frames[page] = True
            timeline.append({"page": page, "frames": list(frames.keys()), "hit": hit})

        return {"algorithm": "LRU", "page_faults": faults, "timeline": timeline, "frames": list(frames.keys())}

    def optimal_faults(self, reference_string):
        frames = []
        faults = 0
        timeline = []

        for index, page in enumerate(reference_string):
            hit = page in frames
            if not hit:
                faults += 1
                if len(frames) < self.frame_count:
                    frames.append(page)
                else:
                    future = reference_string[index + 1 :]
                    victim = None
                    farthest_use = -1
                    for resident in frames:
                        if resident not in future:
                            victim = resident
                            break
                        next_use = future.index(resident)
                        if next_use > farthest_use:
                            farthest_use = next_use
                            victim = resident
                    frames[frames.index(victim)] = page
            timeline.append({"page": page, "frames": list(frames), "hit": hit})

        return {"algorithm": "Optimal", "page_faults": faults, "timeline": timeline, "frames": list(frames)}

    def compare(self, reference_string):
        return {
            "FIFO": self.fifo_faults(reference_string),
            "LRU": self.lru_faults(reference_string),
            "Optimal": self.optimal_faults(reference_string),
        }
