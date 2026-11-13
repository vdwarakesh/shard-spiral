import math

# HyperLogLog is a special type of Probabilistic Structure that estimates the number of unique items (cardinality) in massive datasets using a few kilobytes of RAM by tracking the longest leading-zero streaks in hashed bit strings.
class HyperLogLog(ProbabilisticStructure):
    def __init__(self, b=10):
        super().__init__()
        self.b = b                  # Number of bits used for register indexing (2^b registers)
        self.m = 1 << b             # Total number of registers (e.g., 1024)
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)  # Correction constant