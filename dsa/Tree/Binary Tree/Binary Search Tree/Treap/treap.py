import random

# Treap (Tree + Heap) is a special type of Binary Search Tree that maintains
# BST order on keys and Heap order on randomly assigned priorities simultaneously.
class TreapNode(BinaryTreeNode):
    def __init__(self, key):
        super().__init__(key)
        # Random priority keeps the tree balanced with high probability
        self.priority = random.randint(1, 10**9)


class Treap(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def split(self, node, key):
        # Split the treap into two sub-treaps: keys <= key, and keys > key
        if node is None:
            return None, None
        if node.data <= key:
            left, right = self.split(node.right, key)
            node.right = left
            return node, right
        else:
            left, right = self.split(node.left, key)
            node.left = right
            return left, node