# 2-3-4 Tree is a special type of B-Tree (of minimum degree t=2 / maximum degree 4) where nodes can hold 1, 2, or 3 keys and branch into 2, 3, or 4 children.
# It is perfectly balanced and structurally isomorphic to a Red-Black Tree.
class TwoThreeFourTree(BTree):
    def __init__(self):
        super().__init__(min_degree=2)
        self.max_keys = 3
        self.max_children = 4
        self.attributes = [
            "max_degree_4",
            "perfectly_balanced",
            "multi_way_branching",
            "isomorphic_to_red_black_tree"
        ]