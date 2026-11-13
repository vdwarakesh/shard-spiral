# Compressed Trie is a special type of Trie that collapses chains of single-child nodes into a single edge labeled with a multi-character substring.
class CompressedTrieNode(TrieNode):
    def __init__(self, edge_label=""):
        super().__init__()
        # Multi-character string label along the incoming edge to this node
        self.edge_label = edge_label


class CompressedTrie(Trie):
    def __init__(self):
        super().__init__()
        self.root = CompressedTrieNode()