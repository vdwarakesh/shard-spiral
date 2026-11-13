// SparseTable is a 2D array-based structure that answers idempotent range queries
// (such as Range Minimum Query) in O(1) time over an immutable array.
public class SparseTable {
    // 2D homogeneous integer array storing precomputed interval minimums.
    // (Can also use double[][] or long[][] depending on the array data type).
    protected int[][] st;
    protected int[] logTable;
    protected int n;

    public SparseTable(int[] arr) {
        this.n = arr.length;
        if (this.n == 0) return;

        int maxK = (int) (Math.log(this.n) / Math.log(2)) + 1;
        this.st = new int[maxK][this.n];
        this.logTable = new int[this.n + 1];

        // Precompute logarithms for O(1) lookups during queries
        for (int i = 2; i <= this.n; i++) {
            this.logTable[i] = this.logTable[i / 2] + 1;
        }

        // Initialize base level with raw array values
        for (int i = 0; i < this.n; i++) {
            this.st[0][i] = arr[i];
        }

        // Build the sparse table in O(N log N) time
        for (int k = 1; k < maxK; k++) {
            for (int i = 0; i + (1 << k) <= this.n; i++) {
                this.st[k][i] = Math.min(this.st[k - 1][i], this.st[k - 1][i + (1 << (k - 1))]);
            }
        }
    }
    
    public int queryMin(int left, int right) {
        // Query overlapping blocks in O(1) time
        int k = this.logTable[right - left + 1];
        return Math.min(this.st[k][left], this.st[k][right - (1 << k) + 1]);
    }
}