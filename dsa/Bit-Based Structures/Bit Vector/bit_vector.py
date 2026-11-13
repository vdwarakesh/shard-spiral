# Bit Vector is a special type of Bitset equipped with rank and select directories enabling constant-time O(1) bit counts (Rank) and position lookups (Select).
class BitVector(Bitset):
    def __init__(self, size):
        super().__init__(size)
        self.rank_table = []  # Precomputed superblock rank lookup table for O(1) rank(i)