# XOR Trie (Binary 0-1 Trie) is a special type of Trie that stores integers in their binary form (bit by bit from Most Significant Bit to Least Significant Bit) to rapidly answer maximum/minimum bitwise XOR queries.
class XORTrieNode(TrieNode):
    def __init__(self):
        super().__init__()
        # Fixed two-way branching: index 0 for bit 0, index 1 for bit 1
        self.bit_children = [None, None]


class XORTrie(Trie):
    def __init__(self, max_bits=32):
        super().__init__()
        self.root = XORTrieNode()
        self.max_bits = max_bits  # Number of binary bits per integer (e.g., 32-bit int)

    def insert_number(self, num):
        # Insert integer bit by bit starting from the highest bit down to bit 0
        curr = self.root
        for b in range(self.max_bits - 1, -1, -1):
            bit = (num >> b) & 1
            if curr.bit_children[bit] is None:
                curr.bit_children[bit] = XORTrieNode()
            curr = curr.bit_children[bit]