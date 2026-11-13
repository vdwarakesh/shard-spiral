# Binomial Heap is a special type of Heap composed of a forest of heap-ordered
# Binomial Trees (of power-of-two sizes 2^k), enabling O(log n) heap merges.
class BinomialNode(TreeNode):
    def __init__(self, key):
        super().__init__(key)
        self.degree = 0       # Order k of the binomial tree (tree has 2^k nodes)
        self.parent = None
        self.child = None     # Leftmost child pointer
        self.sibling = None   # Right sibling pointer


class BinomialHeap(Heap):
    def __init__(self):
        super().__init__()
        # Head of the linked root list of Binomial Trees ordered by increasing degree
        self.head_root = None

    def link_trees(self, y, z):
        # Link two Binomial Trees of equal degree k into one tree of degree k + 1
        y.parent = z
        y.sibling = z.child
        z.child = y
        z.degree += 1