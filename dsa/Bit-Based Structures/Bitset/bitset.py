# Bitset is a special type of Bit-Based Structure representing a fixed-size set of bits, supporting fast bitwise AND, OR, XOR, and set membership checks.
class Bitset(BitBasedStructure):
    def __init__(self, size):
        super().__init__(size)
        self.size = size
        # Backed by a large integer manipulated via bitwise shifts
        self.bits = 0

    def set_bit(self, i):
        self.bits |= (1 << i)

    def clear_bit(self, i):
        self.bits &= ~(1 << i)

    def test(self, i):
        return (self.bits & (1 << i)) != 0