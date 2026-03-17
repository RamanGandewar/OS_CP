import time


def auto_save_thread(stop_event, save_callback, enquiry_id, interval=30):
    # Timer-style worker that periodically persists a draft without blocking the UI.
    while not stop_event.wait(interval):
        save_callback(enquiry_id)
        time.sleep(0.05)
