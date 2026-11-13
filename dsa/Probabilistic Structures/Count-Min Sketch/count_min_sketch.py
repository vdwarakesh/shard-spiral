# Count-Min Sketch is a special type of Probabilistic Structure that estimates item frequencies in massive data streams using a 2D grid of counters and multiple hash functions.
class CountMinSketch(ProbabilisticStructure):
    def __init__(self, width, depth):
        super().__init__()
        self.w = width   # Number of counters per hash row
        self.d = depth   # Number of hash rows
        # 2D table of d rows by w columns initialized to zero
        self.table = [[0] * width for _ in range(depth)]

    def add(self, item, count=1):
        for i in range(self.d):
            col = hash((item, i)) % self.w
            self.table[i][col] += count

    def estimate(self, item):
        # Take the minimum counter across all d rows to suppress collision inflation
        return min(self.table[i][hash((item, i)) % self.w] for i in range(self.d))