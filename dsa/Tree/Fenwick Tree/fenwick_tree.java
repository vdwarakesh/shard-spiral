// FenwickTree (Binary Indexed Tree) is a special type of implicit Tree backed by a flat array of size n + 1 that uses bitwise lowbit operations (i & -i) for O(log n) sums.
public class FenwickTree extends Tree {
    // Homogeneous 1-indexed integer array (can also use long[] or double[])
    private final int[] bit;
    private final int n;

    public FenwickTree(int n) {
        super();
        this.n = n;
        this.bit = new int[n + 1];
    }

    public void update(int i, int delta) {
        for (; i <= this.n; i += i & -i) {
            this.bit[i] += delta;
        }
    }

    public int prefixSum(int i) {
        int sum = 0;
        for (; i > 0; i -= i & -i) {
            sum += this.bit[i];
        }
        return sum;
    }
}