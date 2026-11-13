# A Tree is a non-linear hierarchical data structure consisting of nodes connected by edges.
# Every tree starts at a topmost 'root' node, and each node may branch out to zero or more children.
class TreeNode:
    def __init__(self, data):
        self.data = data        # Value stored in the node
        self.children = []      # Dynamic list holding references to child TreeNodes

    def add_child(self, child_node):
        # Connect a child node directly beneath this parent node
        self.children.append(child_node)


class Tree:
    def __init__(self, root_data=None):
        # The root is the starting topmost node of the hierarchy
        self.root = TreeNode(root_data) if root_data is not None else None