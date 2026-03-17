import json
from datetime import datetime


class DashboardWebSocketServer:
    # Lightweight SSE-style publisher used as a no-extra-dependency realtime fallback.
    def __init__(self, snapshot_provider):
        self.snapshot_provider = snapshot_provider

    def event_payload(self):
        return {
            "event": "dashboard_snapshot",
            "generated_at": datetime.utcnow().isoformat(),
            "data": self.snapshot_provider(),
        }

    def sse_message(self):
        payload = json.dumps(self.event_payload())
        return f"event: dashboard_snapshot\ndata: {payload}\n\n"
