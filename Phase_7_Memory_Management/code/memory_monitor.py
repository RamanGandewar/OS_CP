from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from Backend.models import CacheStat, Customer, MemoryPage, Quotation, User, db

from .cache_manager import CacheManager
from .memory_allocator import MemoryAllocator
from .page_replacement import PageReplacement
from .page_table import PageTable


class MemoryMonitor:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_records = self._build_report_records()
        self.page_table = PageTable(self._fetch_report_page, self._persist_page_access, page_size=100, frame_count=5, algorithm="LRU")
        self.cache_manager = CacheManager(self._fetch_customer, self._fetch_quotation, self._fetch_user_pref, self._record_cache_stat)
        self.allocator = MemoryAllocator()
        self.replacement = PageReplacement(frame_count=5)
        self.reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        self.last_comparison = self.replacement.compare(self.reference_string)
        self.last_allocation = None
        self._generate_charts()

    def _build_report_records(self, total=10000):
        return [
            {
                "record_number": index,
                "customer_name": f"Customer {((index % 250) + 1)}",
                "invoice_total": 1500 + (index % 75) * 23,
                "region": ["North", "South", "East", "West"][index % 4],
            }
            for index in range(total)
        ]

    def _fetch_report_page(self, page_number, page_size):
        start = page_number * page_size
        end = start + page_size
        return self.report_records[start:end]

    def _persist_page_access(self, page_number, in_memory=True, increment=True):
        page = MemoryPage.query.filter_by(page_number=page_number).first()
        if not page:
            page = MemoryPage(page_number=page_number)
            db.session.add(page)
        page.touch(in_memory=in_memory, increment=increment)
        db.session.commit()

    def _record_cache_stat(self, cache_type, hits, misses):
        total = hits + misses
        stat = CacheStat(cache_type=cache_type, hits=hits, misses=misses, hit_ratio=(hits / total) if total else 0)
        db.session.add(stat)
        db.session.commit()

    def _fetch_customer(self, customer_id):
        customer = db.session.get(Customer, int(customer_id))
        return customer.to_dict() if customer else None

    def _fetch_quotation(self, quotation_id):
        quotation = db.session.get(Quotation, int(quotation_id))
        return quotation.to_dict() if quotation else None

    def _fetch_user_pref(self, user_id):
        user = db.session.get(User, int(user_id))
        if not user:
            return None
        return {
            "user_id": user.id,
            "dashboard_layout": "analytics-first" if user.role == "admin" else "sales-first",
            "favorite_report": "monthly-sales",
        }

    def load_report_page(self, page_number):
        result = self.page_table.get_page(int(page_number))
        self._generate_charts()
        return result

    def access_customer_cache(self, customer_id):
        result = self.cache_manager.get("customer", int(customer_id))
        self._generate_charts()
        return result

    def access_quotation_cache(self, quotation_id):
        result = self.cache_manager.get("quotation", int(quotation_id))
        self._generate_charts()
        return result

    def access_user_preference_cache(self, user_id):
        result = self.cache_manager.get("user_preference", int(user_id))
        self._generate_charts()
        return result

    def simulate_reference_string(self, reference_string=None, frame_count=5):
        sequence = [int(item) for item in (reference_string or self.reference_string)]
        self.reference_string = sequence
        self.replacement = PageReplacement(frame_count=frame_count)
        self.last_comparison = self.replacement.compare(sequence)
        self._generate_charts()
        return self.last_comparison

    def allocate_memory(self, strategy, size):
        allocation_id = f"{strategy}-{len(self.allocator.allocated) + 1}"
        self.last_allocation = self.allocator.allocate(strategy, int(size), allocation_id)
        self._generate_charts()
        return self.last_allocation

    def reset(self):
        self.page_table.reset()
        self.allocator.reset()
        MemoryPage.query.delete()
        CacheStat.query.delete()
        db.session.commit()
        self.cache_manager.reset()
        self.last_allocation = None
        self.last_comparison = self.replacement.compare(self.reference_string)
        self._generate_charts()

    def get_monitor_payload(self):
        memory_pages = [page.to_dict() for page in MemoryPage.query.order_by(MemoryPage.page_number.asc()).all()]
        cache_stats = {}
        for cache_type in ["customer", "quotation", "user_preference"]:
            latest = CacheStat.query.filter_by(cache_type=cache_type).order_by(CacheStat.id.desc()).first()
            cache_stats[cache_type] = latest.to_dict() if latest else None

        return {
            "page_table": self.page_table.snapshot(total_records=len(self.report_records)),
            "memory_pages": memory_pages,
            "cache": self.cache_manager.snapshot(),
            "cache_stats": cache_stats,
            "allocator": self.allocator.snapshot(),
            "last_allocation": self.last_allocation,
            "replacement_comparison": self.last_comparison,
            "reference_string": self.reference_string,
            "chart_urls": {
                "page_faults": "/api/memory/charts/page-faults",
                "cache_performance": "/api/memory/charts/cache-performance",
                "memory_usage": "/api/memory/charts/memory-usage",
            },
        }

    def chart_path(self, chart_name):
        mapping = {
            "page-faults": self.output_dir / "page_fault_comparison.png",
            "cache-performance": self.output_dir / "cache_performance.png",
            "memory-usage": self.output_dir / "memory_usage.png",
        }
        return mapping.get(chart_name)

    def _generate_charts(self):
        self._generate_page_fault_chart()
        self._generate_cache_chart()
        self._generate_memory_usage_chart()

    def _generate_page_fault_chart(self):
        comparison = self.last_comparison or {}
        algorithms = list(comparison.keys())
        faults = [comparison[name]["page_faults"] for name in algorithms]
        figure, axis = plt.subplots(figsize=(7, 4))
        axis.bar(algorithms, faults, color=["#f4a261", "#2a9d8f", "#264653"])
        axis.set_title("Page Fault Comparison")
        axis.set_ylabel("Fault Count")
        figure.savefig(self.output_dir / "page_fault_comparison.png", bbox_inches="tight")
        plt.close(figure)

    def _generate_cache_chart(self):
        snapshot = self.cache_manager.snapshot()
        cache_names = list(snapshot.keys())
        hit_ratios = [snapshot[name]["hit_ratio"] for name in cache_names]
        figure, axis = plt.subplots(figsize=(7, 4))
        axis.plot(cache_names, hit_ratios, marker="o", linewidth=2, color="#1f7a8c")
        axis.set_ylim(0, 1)
        axis.set_title("Cache Hit Ratio")
        axis.set_ylabel("Hit Ratio")
        figure.savefig(self.output_dir / "cache_performance.png", bbox_inches="tight")
        plt.close(figure)

    def _generate_memory_usage_chart(self):
        snapshot = self.allocator.snapshot()
        values = [snapshot["used_memory"], snapshot["total_free"]]
        labels = ["Used", "Free"]
        figure, axis = plt.subplots(figsize=(7, 4))
        axis.pie(values, labels=labels, autopct="%1.0f%%", colors=["#e76f51", "#e9f5db"])
        axis.set_title("Memory Allocation Usage")
        figure.savefig(self.output_dir / "memory_usage.png", bbox_inches="tight")
        plt.close(figure)
