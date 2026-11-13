# 2-3 Tree is a special type of B-Tree (of maximum degree 3) where every internal node is either a 2-node (1 key, 2 children) or a 3-node (2 keys, 3 children), and all leaves sit at the exact same depth (perfectly balanced).
class TwoThreeTree(BTree):
    def __init__(self):
        # A 2-3 Tree is a B-Tree with max 2 keys and max 3 children per node
        super().__init__(min_degree=2)
        self.attributes = ["max_degree_3", "perfectly_balanced", "multi_way_branching"]