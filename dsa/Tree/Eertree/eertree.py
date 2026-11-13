# Eertree (Palindromic Tree) is a special type of Tree-like structure with two roots
# (length -1 for odd palindromes, length 0 for even palindromes) that stores all distinct palindromic substrings of a string in O(n) space.
class EertreeNode(TreeNode):
    def __init__(self, length):
        super().__init__(length)
        self.length = length      # Length of the palindrome represented by this node
        self.edges = {}           # Edge 'c' transitions from palindrome P to c + P + c
        self.suffix_link = None   # Points to longest proper palindromic suffix


class Eertree(Tree):
    def __init__(self):
        super().__init__()
        # Imaginary root of length -1 (base for 1-letter odd palindromes: -1 + 2 = 1)
        self.odd_root = EertreeNode(-1)
        self.odd_root.suffix_link = self.odd_root
        # Empty-string root of length 0 (base for even palindromes: 0 + 2 = 2)
        self.even_root = EertreeNode(0)
        self.even_root.suffix_link = self.odd_root