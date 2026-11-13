# Hash Map is a special type of Hash Table that maps unique keys to associated values.
# Note: Python's built-in dict is a highly optimized Hash Map:
sample_dict = {"alice": 95, "bob": 88}

# Explicit class implementation inheriting from HashTable:
class HashMap(HashTable):
    def __init__(self, num_buckets=16):
        super().__init__(num_buckets)

    def put(self, key, value):
        # Hash the key to find its bucket; update value if key exists, else append pair
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[idx].append([key, value])

    def get(self, key):
        # Retrieve the value associated with the key in O(1) average time
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                return pair[1]
        return None