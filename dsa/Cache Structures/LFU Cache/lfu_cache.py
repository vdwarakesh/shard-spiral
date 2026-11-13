# LFU Cache (Least Frequently Used) tracks access counts for every item and evicts the item with the lowest request frequency when capacity is reached.
class LFUCache(CacheStructure):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.vals = {}
        self.counts = {}
        self.freqs = collections.defaultdict(OrderedDict)
        self.min_freq = 0