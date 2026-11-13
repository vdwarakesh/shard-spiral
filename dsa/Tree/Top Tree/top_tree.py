# Top Tree is a special type of dynamic Tree that generalizes Link-Cut and Euler Tour Trees by recursively merging connected subtrees ("clusters" with at most 2 boundary vertices) via 'Compress' (joining paths) and 'Rake' (folding side branches) operations.
class ClusterNode(TreeNode):
    def __init__(self, cluster_type, boundary_a, boundary_b=None):
        super().__init__(cluster_type)
        # cluster_type: 'BASE_EDGE', 'COMPRESS' (path merge), or 'RAKE' (branch fold)
        self.cluster_type = cluster_type
        self.boundary_a = boundary_a
        self.boundary_b = boundary_b
        self.left_cluster = None
        self.right_cluster = None


class TopTree(Tree):
    def __init__(self):
        super().__init__()
        self.root_cluster = None