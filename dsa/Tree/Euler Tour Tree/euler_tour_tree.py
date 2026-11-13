# Euler Tour Tree is a special type of dynamic Tree that flattens a tree's Euler tour
# (perimeter depth-first walk) into a balanced sequence BST (like a Treap or Splay Tree), turning whole-subtree queries, links, and cuts into sequence splits and merges.
class EulerTourTree(Tree):
    def __init__(self):
        super().__init__()
        # Sequence BST root storing the flattened Euler tour of the tree
        self.tour_bst_root = None
        # Maps each tree node v to its first and last occurrence in the Euler tour
        self.first_occurrence = {}
        self.last_occurrence = {}