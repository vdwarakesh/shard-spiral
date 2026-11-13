# Hash Set is a special type of Hash Table that stores unique elements only, without associated values, for O(1) average-time membership testing.
# Note: Python's built-in set is a Hash Set:
sample_set = {10, 20, 30}

# Explicit class implementation inheriting from HashTable:
class HashSet(HashTable):
    def __init__(self, num_buckets=16):
        super().__init__(num_buckets)

    def add(self, key):
        # Insert the key only if it is not already present in the bucket
        idx = self._hash(key)
        if key not in self.buckets[idx]:
            self.buckets[idx].append(key)

    def contains(self, key):
        # Check if the key exists in O(1) average time
        idx = self._hash(key)
        return key in self.buckets[idx]