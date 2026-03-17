import threading
from datetime import datetime

from .mutex_manager import SYNC_MONITOR


class SemaphoreManager:
    def __init__(self):
        self.report_semaphore = threading.BoundedSemaphore(3)
        self.db_connection_semaphore = threading.BoundedSemaphore(10)
        self.inventory_lock = threading.Lock()
        self.inventory = {"PRODUCT_X": 5}

    def reserve_inventory(self, product_id, user_id, units=1):
        with self.inventory_lock:
            available = self.inventory.get(product_id, 0)
            if available >= units:
                self.inventory[product_id] = available - units
                SYNC_MONITOR.append_lock_log(
                    f"[{datetime.utcnow().isoformat()}] User {user_id} reserved {units} unit(s) of {product_id}; remaining={self.inventory[product_id]}"
                )
                return {"success": True, "remaining_stock": self.inventory[product_id]}

            SYNC_MONITOR.append_conflict_log(
                f"[{datetime.utcnow().isoformat()}] Oversell prevented for {product_id}; user {user_id} requested {units}, available={available}"
            )
            return {"success": False, "message": "Insufficient stock; semaphore prevented overselling", "remaining_stock": available}

    def acquire_report_slot(self, user_id):
        acquired = self.report_semaphore.acquire(blocking=False)
        if acquired:
            SYNC_MONITOR.append_lock_log(f"[{datetime.utcnow().isoformat()}] User {user_id} acquired report generation slot")
            return {"success": True}
        SYNC_MONITOR.append_conflict_log(f"[{datetime.utcnow().isoformat()}] User {user_id} blocked by report semaphore limit")
        return {"success": False, "message": "Report generation is limited to 3 concurrent jobs"}

    def release_report_slot(self):
        try:
            self.report_semaphore.release()
        except ValueError:
            pass
