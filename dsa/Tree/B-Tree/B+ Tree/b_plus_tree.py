# B+ Tree is a special type of B-Tree where internal nodes store only routing keys, all actual data records live exclusively in the leaf nodes, and leaves are linked sequentially side by side for fast range scans.
class BPlusTreeNode(BTreeNode):
    def __init__(self, is_leaf=True):
        super().__init__(is_leaf)
        self.values = []         # Data payloads stored only when is_leaf is True
        self.next_leaf = None    # Horizontal pointer linking to the next sorted leaf node


class BPlusTree(BTree):
    def __init__(self, min_degree=3):
        super().__init__(min_degree)
        self.root = BPlusTreeNode(is_leaf=True)