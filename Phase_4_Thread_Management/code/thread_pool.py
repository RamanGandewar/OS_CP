from concurrent.futures import ThreadPoolExecutor


class ManagedThreadPool:
    # Reusable worker pool for CRM background jobs.
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="crm-worker")

    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)

    def shutdown(self, wait=False):
        self.executor.shutdown(wait=wait)
