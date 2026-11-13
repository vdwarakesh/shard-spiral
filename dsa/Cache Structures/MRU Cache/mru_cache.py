# MRU Cache (Most Recently Used) evicts the item that was accessed most recently, preventing cache thrashing during sequential scans over datasets larger than RAM.
class MRUCache(CacheStructure):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.od = OrderedDict()

    def put(self, key, value):
        if key in self.od:
            self.od.move_to_end(key)
        self.od[key] = value
        if len(self.od) > self.capacity:
            # Evict the most recently used item from the back end instead of the front
            self.od.popitem(last=True)