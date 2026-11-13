# Fenwick Tree (Binary Indexed Tree / BIT) is a special type of implicit Tree stored inside a 1-indexed flat array that uses lowest-set-bit jumps (i & -i) to perform prefix sums and point updates in O(log n) time.
class FenwickTree(Tree):
    def __init__(self, size):
        super().__init__()
        self.size = size
        # 1-indexed array where bit[i] stores the sum of (i & -i) elements ending at i
        self.bit = [0] * (size + 1)

    def update(self, i, delta):
        # Add delta to index i and all ancestor intervals covering i
        while i <= self.size:
            self.bit[i] += delta
            i += i & (-i)  # Jump up to parent by adding Lowest Significant Bit

    def prefix_sum(self, i):
        # Sum elements from 1 to i by stripping off Lowest Significant Bits
        total = 0
        while i > 0:
            total += self.bit[i]
            i -= i & (-i)
        return total