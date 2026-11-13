// CountingBloomFilter is a special type of BloomFilter that uses integer counters instead of single bits, permitting item deletions.
public class CountingBloomFilter extends BloomFilter {
    protected int[] counters; // Tally counters replacing single bits

    public CountingBloomFilter(int capacity, double fpRate) {
        super(capacity, fpRate);
        this.counters = new int[this.m];
    }

    public void remove(String item) {
        for (int seed = 0; seed < this.k; seed++) {
            int idx = Math.abs((item + seed).hashCode()) % this.m;
            if (this.counters[idx] > 0) this.counters[idx]--;
        }
    }
}