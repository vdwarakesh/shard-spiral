// DynamicSegmentTree is a special type of SegmentTree that creates nodes lazily on demand, handling huge sparse coordinate ranges (e.g., [0, 10^18]) without pre-allocating 4N space.
public class DynamicSegmentTree extends SegmentTree {
    protected long minCoord;
    protected long maxCoord;

    public DynamicSegmentTree(long minCoord, long maxCoord) {
        super(new int[0]);
        this.minCoord = minCoord;
        this.maxCoord = maxCoord;
        this.binaryRoot = new BinaryNode(0);
    }

    public void update(BinaryNode node, long start, long end, long idx, int val) {
        if (start == end) {
            node.data += val;
            return;
        }
        long mid = start + (end - start) / 2;
        if (idx <= mid) {
            if (node.left == null) node.left = new BinaryNode(0); // Lazy node creation
            update(node.left, start, mid, idx, val);
        } else {
            if (node.right == null) node.right = new BinaryNode(0);
            update(node.right, mid + 1, end, idx, val);
        }
        node.data = (node.left != null ? node.left.data : 0)
                  + (node.right != null ? node.right.data : 0);
    }
}