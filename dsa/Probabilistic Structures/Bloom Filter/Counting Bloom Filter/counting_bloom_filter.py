# Counting Bloom Filter is a special type of Bloom Filter that replaces single bits with multi-bit tally counters, unlocking full support for safe item deletions.
class CountingBloomFilter(BloomFilter):
    def __init__(self, capacity, false_positive_rate=0.01):
        super().__init__(capacity, false_positive_rate)
        # Replace 1-bit flags with integer counters (e.g., 4-bit nibbles)
        self.counters = [0] * self.m

    def add(self, item):
        for seed in range(self.k):
            idx = hash((item, seed)) % self.m
            self.counters[idx] += 1

    def remove(self, item):
        # Safely decrement counters without breaking other overlapping items
        for seed in range(self.k):
            idx = hash((item, seed)) % self.m
            if self.counters[idx] > 0:
                self.counters[idx] -= 1