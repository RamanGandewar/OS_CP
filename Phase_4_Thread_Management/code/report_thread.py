import time


def report_generation_thread(payload, complete_callback):
    # Background worker for long-running report preparation.
    duration = int(payload.get("duration", 3))
    time.sleep(max(duration, 1))
    complete_callback(payload)
