import math

# Sparse Table is a 2D array-based data structure built over an immutable (static) array.
# It precalculates answers for intervals of power-of-two lengths, enabling O(1)  constant-time queries for overlapping operations like Range Minimum or Maximum.
class SparseTable:
    def __init__(self, arr):
        self.n = len(arr)
        if self.n == 0:
            return
            
        self.max_k = int(math.log2(self.n)) + 1
        # st[k][i] stores the minimum for the interval starting at index i with length 2^k
        self.st = [[0] * self.n for _ in range(self.max_k)]

        # Base case: intervals of length 2^0 = 1 are just the array elements themselves
        for i in range(self.n):
            self.st[0][i] = arr[i]

        # Dynamic Programming: Build higher levels using the previous lower level
        for k in range(1, self.max_k):
            # 1 << k is equivalent to 2^k
            for i in range(self.n - (1 << k) + 1):
                # The minimum of a block of size 2^k is the minimum of two overlapping  or adjacent blocks of size 2^(k-1)
                self.st[k][i] = min(self.st[k - 1][i], self.st[k - 1][i + (1 << (k - 1))])

    def query_min(self, left, right):
        # O(1) Range Minimum Query overlapping two precomputed blocks
        length = right - left + 1
        k = int(math.log2(length))
        return min(self.st[k][left], self.st[k][right - (1 << k) + 1])