// BTree is a special type of self-balancing Tree where each node holds multiple sorted keys and branches into up to 2t children, minimizing disk I/O reads.
public class BTree extends Tree {
    public static class BNode extends TreeNode {
        // Homogeneous array of sorted keys (can also use Comparable Objects)
        public int[] keys;
        // Array of child node references
        public BNode[] childNodes;
        public int numKeys;
        public boolean isLeaf;

        public BNode(int t, boolean isLeaf) {
            super(0);
            this.isLeaf = isLeaf;
            this.keys = new int[2 * t - 1];     // Max 2t - 1 keys per node
            this.childNodes = new BNode[2 * t]; // Max 2t children per node
            this.numKeys = 0;
        }
    }

    protected int t; // Minimum degree of the B-Tree
    protected BNode bRoot;

    public BTree(int t) {
        super();
        this.t = t;
        this.bRoot = new BNode(t, true);
    }
}