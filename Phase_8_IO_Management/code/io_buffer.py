class IOBufferPool:
    def __init__(self, buffer_count=4, buffer_size=256):
        self.buffer_count = buffer_count
        self.buffer_size = buffer_size
        self.buffers = [{"buffer_id": index, "used": 0, "status": "FREE"} for index in range(buffer_count)]
        self.history = []

    def allocate(self, request_type, size):
        for buffer in self.buffers:
            if buffer["status"] == "FREE" and size <= self.buffer_size:
                buffer["used"] = size
                buffer["status"] = "ALLOCATED"
                event = {"action": "allocate", "buffer_id": buffer["buffer_id"], "request_type": request_type, "size": size}
                self.history.append(event)
                return {"success": True, **event}
        event = {"action": "allocate_failed", "request_type": request_type, "size": size}
        self.history.append(event)
        return {"success": False, **event}

    def release(self, buffer_id):
        for buffer in self.buffers:
            if buffer["buffer_id"] == buffer_id:
                buffer["used"] = 0
                buffer["status"] = "FREE"
                event = {"action": "release", "buffer_id": buffer_id}
                self.history.append(event)
                return {"success": True, **event}
        return {"success": False, "message": "Buffer not found"}

    def snapshot(self):
        return {
            "buffer_count": self.buffer_count,
            "buffer_size": self.buffer_size,
            "buffers": self.buffers,
            "history": self.history[-20:],
        }
