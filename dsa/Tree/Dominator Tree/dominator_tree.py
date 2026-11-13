# Dominator Tree is a special type of directed Tree built from a flow graph where every node's parent is its Immediate Dominator (idom)-the closest mandatory checkpoint that every path from the entry root R to that node must pass through.
class DominatorTree(Tree):
    def __init__(self, num_vertices, entry_root=0):
        super().__init__(entry_root)
        self.num_vertices = num_vertices
        self.entry_root = entry_root
        # idom[v] stores the Immediate Dominator (parent in Dominator Tree) of vertex v
        self.idom = [-1] * num_vertices
        self.idom[entry_root] = entry_root
        # Adjacency list of the resulting Dominator Tree hierarchy
        self.dom_tree_children = [[] for _ in range(num_vertices)]