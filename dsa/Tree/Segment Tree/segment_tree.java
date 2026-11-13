// SegmentTree is a special type of BinaryTree that partitions an array into hierarchical intervals to answer range queries and point/range updates in O(log n) time.
public class SegmentTree extends BinaryTree {
    // Homogeneous integer array of size 4n storing interval aggregates.
    // Note: Can also hold custom objects/structs for complex range queries.
    protected int[] segTree;
    protected int n;

    public SegmentTree(int[] arr) {
        super();
        this.n = arr.length;
        this.segTree = new int[4 * n];
        if (n > 0) {
            build(arr, 1, 0, n - 1);
        }
    }

    protected void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            this.segTree[node] = arr[start];
            return;
        }
        int mid = (start + end) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        this.segTree[node] = this.segTree[2 * node] + this.segTree[2 * node + 1];
    }
}