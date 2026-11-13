# Hash Table is a special type of Hash-Based Structure that stores data in an array of buckets and resolves hash collisions (here via separate chaining).
class HashTable(HashBasedStructure):
    def __init__(self, num_buckets=16):
        super().__init__(num_buckets)
        # Array of buckets; each bucket holds a list of colliding entries
        self.buckets = [[] for _ in range(num_buckets)]