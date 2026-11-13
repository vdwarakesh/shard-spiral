# Binary Tree is a special type of Tree in which every node has at most two children: explicitly designated as the 'left' child and the 'right' child.
class BinaryTreeNode(TreeNode):
    def __init__(self, data):
        super().__init__(data)
        self.left = None   # Pointer to the left child node
        self.right = None  # Pointer to the right child node


class BinaryTree(Tree):
    def __init__(self, root_data=None):
        super().__init__()
        self.root = BinaryTreeNode(root_data) if root_data is not None else None