// Base class for Bit-Based Structures that operate on individual bits of machine words.
public class BitBasedStructures {
    protected int bitWord; // 32-bit or 64-bit word packing boolean flags

    public BitBasedStructures() {
        this.bitWord = 0;
    }
}