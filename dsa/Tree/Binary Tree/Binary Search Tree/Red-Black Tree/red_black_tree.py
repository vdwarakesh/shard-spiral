# Red-Black Tree is a special type of Binary Search Tree that colors each node
# Red or Black and enforces color invariants so no path is more than twice as long as another.
class RedBlackNode(BinaryTreeNode):
    def __init__(self, data, is_red=True):
        super().__init__(data)
        self.is_red = is_red  # True = Red, False = Black; new nodes default to Red
        self.parent = None    # Parent pointer used during recoloring and rotations


class RedBlackTree(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def insert_root(self, data):
        # Rule 1 of Red-Black Trees: The root node must always be colored Black
        self.root = RedBlackNode(data, is_red=False)