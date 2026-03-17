from collections import OrderedDict
from datetime import datetime


class LRUEntityCache:
    def __init__(self, cache_type, maxsize, fetcher, stats_callback):
        self.cache_type = cache_type
        self.maxsize = maxsize
        self.fetcher = fetcher
        self.stats_callback = stats_callback
        self.store = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.last_access = []

    def get(self, key):
        timestamp = datetime.utcnow().isoformat()
        if key in self.store:
            self.hits += 1
            self.store.move_to_end(key)
            value = self.store[key]
            result = {"cache_type": self.cache_type, "hit": True, "value": value, "timestamp": timestamp}
        else:
            self.misses += 1
            value = self.fetcher(key)
            if value is None:
                value = {"id": key, "message": "Not found"}
            if len(self.store) >= self.maxsize:
                self.store.popitem(last=False)
            self.store[key] = value
            result = {"cache_type": self.cache_type, "hit": False, "value": value, "timestamp": timestamp}

        self.last_access.append({"key": key, "hit": result["hit"], "timestamp": timestamp})
        self.stats_callback(self.cache_type, self.hits, self.misses)
        return result

    def reset(self):
        self.store.clear()
        self.hits = 0
        self.misses = 0
        self.last_access = []
        self.stats_callback(self.cache_type, self.hits, self.misses)

    def snapshot(self):
        total = self.hits + self.misses
        return {
            "cache_type": self.cache_type,
            "size": len(self.store),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": round(self.hits / total, 4) if total else 0,
            "keys": list(self.store.keys()),
            "recent_access": self.last_access[-10:],
        }


class CacheManager:
    def __init__(self, customer_fetcher, quotation_fetcher, user_pref_fetcher, stats_callback):
        self.caches = {
            "customer": LRUEntityCache("customer", 100, customer_fetcher, stats_callback),
            "quotation": LRUEntityCache("quotation", 50, quotation_fetcher, stats_callback),
            "user_preference": LRUEntityCache("user_preference", 25, user_pref_fetcher, stats_callback),
        }

    def get(self, cache_type, key):
        return self.caches[cache_type].get(key)

    def reset(self):
        for cache in self.caches.values():
            cache.reset()

    def snapshot(self):
        return {cache_type: cache.snapshot() for cache_type, cache in self.caches.items()}
