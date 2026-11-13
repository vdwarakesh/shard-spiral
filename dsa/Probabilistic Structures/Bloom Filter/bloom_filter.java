// BloomFilter is a special type of ProbabilisticStructures providing O(1) set membership tests with zero false negatives and tunable false-positive rates.
public class BloomFilter extends ProbabilisticStructures {
    protected int[] bitArray;
    protected int m; // Bit array size
    protected int k; // Number of hash functions

    public BloomFilter(int capacity, double fpRate) {
        super(fpRate);
        this.m = (int) (-capacity * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        this.k = Math.max(1, (int) ((double) m / capacity * Math.log(2)));
        this.bitArray = new int[m];
    }
}