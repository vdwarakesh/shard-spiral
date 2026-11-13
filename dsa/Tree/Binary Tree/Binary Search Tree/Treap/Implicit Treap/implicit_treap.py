# Implicit Treap is a special type of Treap that uses each node's dynamic array position (computed on the fly from subtree sizes) as its implicit BST key.
class ImplicitTreapNode(TreapNode):
    def __init__(self, value):
        super().__init__(value)
        # Subtree size replaces explicit keys so array indices are calculated dynamically
        self.size = 1


class ImplicitTreap(Treap):
    def __init__(self):
        super().__init__()

    def _get_size(self, node):
        return node.size if node else 0

    def _update_size(self, node):
        # Recalculate implicit index counts after splits or merges
        if node:
            node.size = 1 + self._get_size(node.left) + self._get_size(node.right)