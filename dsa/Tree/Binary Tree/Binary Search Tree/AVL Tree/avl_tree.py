# AVL Tree is a special type of Binary Search Tree that strictly self-balances so the heights of the left and right subtrees of any node never differ by more than 1.
class AVLNode(BinaryTreeNode):
    def __init__(self, data):
        super().__init__(data)
        self.height = 1  # Track node height to compute balance factors in O(1) time


class AVLTree(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        # Balance factor must remain in {-1, 0, +1}; otherwise rotations are triggered
        return self._height(node.left) - self._height(node.right) if node else 0

    def _rotate_right(self, y):
        # Right rotation around unbalanced node y to lift its left child x
        x = y.left
        t2 = x.right
        x.right = y
        y.left = t2
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        return x