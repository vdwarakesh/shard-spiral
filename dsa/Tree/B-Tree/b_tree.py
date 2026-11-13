# B-Tree is a special type of self-balancing search Tree that stores multiple sorted keys in every node and branches into multiple children, keeping the tree wide and shallow.
class BTreeNode(TreeNode):
    def __init__(self, is_leaf=True):
        super().__init__(None)
        self.keys = []       # Sorted list of keys stored inside this node
        self.children = []   # List of child BTreeNode pointers (len(children) == len(keys) + 1)
        self.is_leaf = is_leaf


class BTree(Tree):
    def __init__(self, min_degree=3):
        super().__init__()
        # Minimum degree 't': every node (except root) holds between t-1 and 2t-1 keys
        self.t = min_degree
        self.root = BTreeNode(is_leaf=True)