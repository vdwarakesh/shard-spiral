# Order Statistic Tree is a special type of Binary Search Tree augmented with subtree sizes in every node to answer k-th smallest (select) and rank queries in O(log n).
class OrderStatisticNode(BinaryTreeNode):
    def __init__(self, key):
        super().__init__(key)
        self.size = 1  # Total nodes in the subtree rooted at this node


class OrderStatisticTree(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def size(self, node):
        return node.size if node else 0

    def select_kth(self, node, k):
        # Find the k-th smallest element (0-indexed) using left subtree size
        if node is None:
            return None
        left_size = self.size(node.left)
        if k == left_size:
            return node.data
        elif k < left_size:
            return self.select_kth(node.left, k)
        else:
            return self.select_kth(node.right, k - left_size - 1)