# Segment Tree is a special type of Binary Tree that stores precomputed interval summaries (such as range sums, mins, or maxes) to support O(log n) range queries and updates.
class SegmentTree(BinaryTree):
    def __init__(self, arr):
        super().__init__()
        self.n = len(arr)
        # Flat array of size 4*n representing the complete binary segment tree
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node, start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        # Internal node stores the merged summary of its left and right child segments
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]