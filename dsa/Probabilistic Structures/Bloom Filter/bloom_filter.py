import math

# Bloom Filter is a special type of Probabilistic Structure that tests set membership with zero false negatives and a small tunable false-positive probability.
class BloomFilter(ProbabilisticStructure):
    def __init__(self, capacity, false_positive_rate=0.01):
        super().__init__(false_positive_rate)
        # Optimal bit array size m and hash function count k calculation
        self.m = int(-capacity * math.log(false_positive_rate) / (math.log(2) ** 2))
        self.k = int((self.m / capacity) * math.log(2))
        self.bit_array = [0] * self.m

    def add(self, item):
        # Set k hashed bit positions to 1
        for seed in range(self.k):
            idx = hash((item, seed)) % self.m
            self.bit_array[idx] = 1