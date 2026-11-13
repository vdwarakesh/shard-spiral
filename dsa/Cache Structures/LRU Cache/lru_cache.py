from collections import OrderedDict

# LRU Cache (Least Recently Used) evicts the item that has gone the longest time without being accessed when capacity is exceeded.
class LRUCache(CacheStructure):
    def __init__(self, capacity):
        super().__init__(capacity)
        # OrderedDict maintains insertion/access order for O(1) LRU eviction
        self.od = OrderedDict()

    def get(self, key):
        if key not in self.od:
            return -1
        self.od.move_to_end(key)  # Mark as recently used
        return self.od[key]

    def put(self, key, value):
        if key in self.od:
            self.od.move_to_end(key)
        self.od[key] = value
        if len(self.od) > self.capacity:
            self.od.popitem(last=False)  # Evict stalest item from the front tail