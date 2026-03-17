class MemoryAllocator:
    def __init__(self, blocks=None):
        self.initial_blocks = list(blocks or [120, 260, 80, 300, 150, 90])
        self.reset()

    def reset(self):
        self.memory_blocks = list(self.initial_blocks)
        self.allocated = {}
        self.next_fit_index = 0

    def allocate(self, strategy, size, allocation_id):
        strategy = strategy.lower()
        selector = {
            "first_fit": self.first_fit,
            "best_fit": self.best_fit,
            "worst_fit": self.worst_fit,
            "next_fit": self.next_fit,
        }.get(strategy)
        if not selector:
            return {"success": False, "message": "Unknown allocation strategy"}
        block_index = selector(size)
        if block_index is None:
            return {"success": False, "message": "No memory block can satisfy this allocation request"}
        before = self.memory_blocks[block_index]
        self.memory_blocks[block_index] -= size
        self.allocated[allocation_id] = {"size": size, "block_index": block_index, "strategy": strategy}
        return {
            "success": True,
            "allocation_id": allocation_id,
            "strategy": strategy,
            "block_index": block_index,
            "before": before,
            "after": self.memory_blocks[block_index],
        }

    def first_fit(self, size):
        for index, block in enumerate(self.memory_blocks):
            if block >= size:
                return index
        return None

    def best_fit(self, size):
        candidates = [(index, block) for index, block in enumerate(self.memory_blocks) if block >= size]
        return min(candidates, key=lambda item: item[1])[0] if candidates else None

    def worst_fit(self, size):
        candidates = [(index, block) for index, block in enumerate(self.memory_blocks) if block >= size]
        return max(candidates, key=lambda item: item[1])[0] if candidates else None

    def next_fit(self, size):
        count = len(self.memory_blocks)
        for offset in range(count):
            index = (self.next_fit_index + offset) % count
            if self.memory_blocks[index] >= size:
                self.next_fit_index = index
                return index
        return None

    def snapshot(self):
        return {
            "free_blocks": self.memory_blocks,
            "allocated": self.allocated,
            "total_free": sum(self.memory_blocks),
            "used_memory": sum(item["size"] for item in self.allocated.values()),
        }
