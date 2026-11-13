# Binary Search Tree (BST) is a special type of Binary Tree that maintains the ordering invariant: all keys in the left subtree are smaller than the node's key, and all keys in the right subtree are larger.
class BinarySearchTree(BinaryTree):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        # Insert value while preserving the left < parent < right ordering property
        self.root = self._insert_recursive(self.root, data)

    def _insert_recursive(self, node, data):
        if node is None:
            return BinaryTreeNode(data)
        if data < node.data:
            node.left = self._insert_recursive(node.left, data)
        elif data > node.data:
            node.right = self._insert_recursive(node.right, data)
        return node