import time


def notification_thread(stop_event, send_callback, interval=60):
    # Daemon service that checks for pending notifications and sends them asynchronously.
    while not stop_event.wait(interval):
        send_callback()
        time.sleep(0.05)
