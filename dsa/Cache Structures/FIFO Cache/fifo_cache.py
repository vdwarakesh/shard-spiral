from collections import deque

# FIFO Cache (First-In, First-Out) evicts items strictly in chronological order of their arrival time, providing lock-free read performance.
class FIFOCache(CacheStructure):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.cache_map = {}
        self.queue = deque()

    def put(self, key, value):
        if key not in self.cache_map:
            if len(self.queue) >= self.capacity:
                oldest_key = self.queue.popleft()
                del self.cache_map[oldest_key]
            self.queue.append(key)
        self.cache_map[key] = value