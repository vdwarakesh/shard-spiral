# Persistent Segment Tree is a special type of Segment Tree that preserves every historical version of the tree after updates by path-copying only the O(log n) modified nodes.
class PersistentSegNode(BinaryTreeNode):
    def __init__(self, val=0, left=None, right=None):
        super().__init__(val)
        self.left = left
        self.right = right


class PersistentSegmentTree(SegmentTree):
    def __init__(self, n):
        super().__init__([])
        self.n = n
        # List of root pointers; roots[v] accesses the complete segment tree at version v
        self.version_roots = []

    def update_version(self, prev_root, start, end, idx, val):
        # Allocate a brand-new node along the modified path while sharing untouched subtrees
        if start == end:
            return PersistentSegNode(val)
        mid = (start + end) // 2
        left_child = prev_root.left if prev_root else None
        right_child = prev_root.right if prev_root else None
        if idx <= mid:
            new_left = self.update_version(left_child, start, mid, idx, val)
            return PersistentSegNode((new_left.data if new_left else 0) + (right_child.data if right_child else 0),
                                     new_left, right_child)
        else:
            new_right = self.update_version(right_child, mid + 1, end, idx, val)
            return PersistentSegNode((left_child.data if left_child else 0) + (new_right.data if new_right else 0),
                                     left_child, new_right)