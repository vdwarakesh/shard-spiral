# Link-Cut Tree is a special type of dynamic Tree structure that decomposes a forest of trees into "preferred paths" maintained inside auxiliary Splay Trees, supporting
# O(log n) amortized path aggregates, dynamic edge linking, and edge cutting.
class LinkCutNode(BinaryTreeNode):
    def __init__(self, value=0):
        super().__init__(value)
        self.parent = None       # Splay tree parent OR path-parent pointer across preferred paths
        self.rev_lazy = False    # Lazy reversal flag used when re-rooting a tree


class LinkCutTree(Tree):
    def __init__(self, n):
        super().__init__()
        # Forest of n LinkCutNodes that can be dynamically linked and cut
        self.nodes = [LinkCutNode(i) for i in range(n)]

    def is_splay_root(self, x):
        # A node is the root of its auxiliary splay tree if its parent does not point back to it
        return x.parent is None or (x.parent.left != x and x.parent.right != x)