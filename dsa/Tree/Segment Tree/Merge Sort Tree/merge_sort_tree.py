# Merge Sort Tree is a special type of Segment Tree in which every node stores a complete sorted list of all elements within its interval, enabling binary search over subarrays.
class MergeSortTree(SegmentTree):
    def __init__(self, arr):
        super().__init__([])
        self.n = len(arr)
        # Each node holds a sorted Python list of the elements in its interval
        self.tree = [[] for _ in range(4 * self.n)]
        if self.n > 0:
            self._build_sorted(arr, 1, 0, self.n - 1)

    def _build_sorted(self, arr, node, start, end):
        if start == end:
            self.tree[node] = [arr[start]]
            return
        mid = (start + end) // 2
        self._build_sorted(arr, 2 * node, start, mid)
        self._build_sorted(arr, 2 * node + 1, mid + 1, end)
        # Merge the two sorted child lists into the parent node's sorted list
        self.tree[node] = sorted(self.tree[2 * node] + self.tree[2 * node + 1])