# Dynamic Segment Tree (Sparse Segment Tree) is a special type of Segment Tree that allocates child nodes lazily on demand only when an interval is actually touched, allowing it to span massive coordinate ranges like [0, 10^18].
class DynamicSegmentTree(SegmentTree):
    def __init__(self, min_coord=0, max_coord=10**9):
        super().__init__([])
        self.min_coord = min_coord
        self.max_coord = max_coord
        self.root = BinaryTreeNode(0)

    def update(self, node, start, end, idx, val):
        if start == end:
            node.data += val
            return
        mid = (start + end) // 2
        if idx <= mid:
            # Lazily allocate left child only when needed
            if node.left is None:
                node.left = BinaryTreeNode(0)
            self.update(node.left, start, mid, idx, val)
        else:
            # Lazily allocate right child only when needed
            if node.right is None:
                node.right = BinaryTreeNode(0)
            self.update(node.right, mid + 1, end, idx, val)
        node.data = (node.left.data if node.left else 0) + (node.right.data if node.right else 0)