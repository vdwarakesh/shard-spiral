# Splay Tree is a special type of Binary Search Tree that automatically moves any recently accessed or inserted node all the way to the root via splay rotations.
class SplayTree(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def _rotate_right(self, x):
        # Zig step (single right rotation) moving left child y up toward the root
        y = x.left
        x.left = y.right
        y.right = x
        return y

    def _rotate_left(self, x):
        # Zag step (single left rotation) moving right child y up toward the root
        y = x.right
        x.right = y.left
        y.left = x
        return y