import java.util.ArrayList;
import java.util.List;

// PersistentSegmentTree is a special type of SegmentTree that retains all historical versions after point updates by creating new nodes only along the O(log n) modified path.
public class PersistentSegmentTree extends SegmentTree {
    public static class PersistentNode extends BinaryNode {
        public PersistentNode(int sum, BinaryNode left, BinaryNode right) {
            super(sum);
            this.left = left;
            this.right = right;
        }
    }

    // Stores the root node of every historical version
    protected List<PersistentNode> versionRoots = new ArrayList<>();

    public PersistentSegmentTree(int n) {
        super(new int[0]);
        this.n = n;
    }
}