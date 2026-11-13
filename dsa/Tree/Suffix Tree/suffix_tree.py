# Suffix Tree is a special type of Tree (specifically a compressed Suffix Trie) that stores all suffixes of a string in O(n) space by labeling edges with [start, end] index pairs into the original string instead of copying characters.
class SuffixTreeNode(TreeNode):
    def __init__(self, start=-1, end=-1):
        super().__init__(None)
        self.start = start          # Starting index of edge substring in the master text
        self.end = end              # Ending index of edge substring in the master text
        self.children = {}          # Maps starting character -> SuffixTreeNode
        self.suffix_link = None     # Shortcut pointer used in Ukkonen's O(n) construction


class SuffixTree(Tree):
    def __init__(self, text=""):
        super().__init__()
        self.text = text
        self.root = SuffixTreeNode()