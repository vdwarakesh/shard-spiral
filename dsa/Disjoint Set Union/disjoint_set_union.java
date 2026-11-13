// DisjointSetUnion (Union-Find) maintains non-overlapping groups with path compression and union by rank for nearly instantaneous connectivity checks.
public class DisjointSetUnion {
    // Homogeneous array storing parent set pointers (can also be Object[] for generic types)
    protected int[] parent;
    protected int[] rank;

    public DisjointSetUnion(int n) {
        this.parent = new int[n];
        this.rank = new int[n];
        for (int i = 0; i < n; i++) {
            this.parent[i] = i; // Each element starts as its own set leader
            this.rank[i] = 0;
        }
    }

    public int find(int i) {
        if (this.parent[i] != i) {
            this.parent[i] = find(this.parent[i]); // Path compression
        }
        return this.parent[i];
    }

    public void union(int i, int j) {
        int rootI = find(i);
        int rootJ = find(j);
        if (rootI != rootJ) {
            if (this.rank[rootI] < this.rank[rootJ]) {
                this.parent[rootI] = rootJ;
            } else if (this.rank[rootI] > this.rank[rootJ]) {
                this.parent[rootJ] = rootI;
            } else {
                this.parent[rootJ] = rootI;
                this.rank[rootI]++;
            }
        }
    }
}