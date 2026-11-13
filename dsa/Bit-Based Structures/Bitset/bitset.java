// Bitset is a special type of BitBasedStructures mapping a fixed range of integers to compact bits inside an array of 64-bit words.
public class Bitset extends BitBasedStructures {
    protected long[] words;
    protected int numBits;

    public Bitset(int size) {
        super();
        this.numBits = size;
        this.words = new long[(size + 63) / 64];
    }

    public void set(int i) {
        this.words[i / 64] |= (1L << (i % 64));
    }

    public boolean test(int i) {
        return (this.words[i / 64] & (1L << (i % 64))) != 0;
    }
}