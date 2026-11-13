// BPlusTree is a special type of BTree that stores all data values in the bottom leaf layer and links all leaf nodes into a sequential chain for fast range queries.
public class BPlusTree extends BTree {
    public static class BPlusNode extends BNode {
        // Homogeneous array of data payloads stored at leaf nodes (can hold any Object/Record)
        public Object[] values;
        // Sibling pointer connecting leaf nodes sequentially
        public BPlusNode nextLeaf;

        public BPlusNode(int t, boolean isLeaf) {
            super(t, isLeaf);
            this.values = isLeaf ? new Object[2 * t - 1] : null;
            this.nextLeaf = null;
        }
    }

    public BPlusTree(int t) {
        super(t);
        this.bRoot = new BPlusNode(t, true);
    }
}