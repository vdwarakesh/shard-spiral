# Hash-Based Structures organize and locate data in O(1) average time by converting keys into array bucket indices using a deterministic hash function.
class HashBasedStructure:
    def __init__(self, num_buckets=16):
        self.num_buckets = num_buckets

    def _hash(self, key):
        # Transform an arbitrary key into a valid bucket index [0, num_buckets - 1]
        return hash(key) % self.num_buckets