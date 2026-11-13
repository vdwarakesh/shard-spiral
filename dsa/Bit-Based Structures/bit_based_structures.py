# Bit-Based Structures pack boolean flags and sets into individual binary bits within machine words for 8x-64x memory savings and hardware bitwise parallelism.
class BitBasedStructure:
    def __init__(self, size_in_bits):
        self.size = size_in_bits
        # Stored as an integer where individual bits represent boolean states
        self.bit_word = 0