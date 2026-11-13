# Trie (Prefix Tree) is a special type of Tree that stores strings character by character along its edges so strings with a common prefix share the exact same path from the root.
class TrieNode(TreeNode):
    def __init__(self):
        super().__init__(None)
        self.children = {}     # Maps character -> child TrieNode
        self.is_end = False    # True if path from root spells a complete inserted word


class Trie(Tree):
    def __init__(self):
        super().__init__()
        self.root = TrieNode()

    def insert(self, word):
        # Walk character by character from the root, creating nodes as needed
        curr = self.root
        for ch in word:
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        curr.is_end = True