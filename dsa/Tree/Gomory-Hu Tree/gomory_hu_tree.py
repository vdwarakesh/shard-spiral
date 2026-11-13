# Gomory-Hu Tree (Cut Tree) is a special type of weighted Tree built over V vertices of an undirected graph that encodes the Minimum s-t Cut (Max Flow) between all
# V*(V-1)/2 vertex pairs using only V - 1 weighted tree edges.
class GomoryHuTree(Tree):
    def __init__(self, num_vertices):
        super().__init__()
        self.num_vertices = num_vertices
        # parent[v] stores the parent of vertex v in the Gomory-Hu Cut Tree
        self.parent = [0] * num_vertices
        # min_cut_weight[v] stores the capacity of the tree edge (v, parent[v])
        self.min_cut_weight = [0] * num_vertices