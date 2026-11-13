// BitVector is a special type of Bitset augmented with superblock lookup directories for constant-time O(1) Rank and Select operations.
public class BitVector extends Bitset {
    protected int[] rankSuperblocks;

    public BitVector(int size) {
        super(size);
        this.rankSuperblocks = new int[(size + 511) / 512];
    }
}