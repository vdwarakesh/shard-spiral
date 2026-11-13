# Patricia Trie is a special type of Compressed Trie (specifically a radix-2 binary radix tree) where each internal node stores the exact bit index where keys first differ, skipping all identical intermediate bits completely.
class PatriciaTrieNode(CompressedTrieNode):
    def __init__(self, bit_index=-1, key=None):
        super().__init__()
        self.bit_index = bit_index  # Critical bit offset to test next (0 goes left, 1 goes right)
        self.key = key              # Full key stored at terminal nodes for final verification
        self.left = None            # Branch for bit 0
        self.right = None           # Branch for bit 1


class PatriciaTrie(CompressedTrie):
    def __init__(self):
        super().__init__()
        self.root = PatriciaTrieNode()