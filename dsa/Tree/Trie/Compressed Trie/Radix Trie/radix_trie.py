# Radix Trie (Radix Tree) is a special type of Compressed Trie that chunks keys by a fixed radix (base) and maps compressed prefix edges to child subtrees.
class RadixTrieNode(CompressedTrieNode):
    def __init__(self, prefix="", is_end=False):
        super().__init__(prefix)
        self.is_end = is_end
        # Maps the first character of a compressed edge to its child RadixTrieNode
        self.edges = {}


class RadixTrie(CompressedTrie):
    def __init__(self):
        super().__init__()
        self.root = RadixTrieNode()