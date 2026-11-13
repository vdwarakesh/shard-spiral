// LinkCutTree is a special type of dynamic Tree that partitions trees into preferred paths backed by Splay Trees to support O(log n) Link, Cut, and root-path queries.
public class LinkCutTree extends Tree {
    public static class LCTNode extends TreeNode {
        public LCTNode left;
        public LCTNode right;
        public LCTNode parent;  // Serves as both Splay parent and Path-Parent pointer
        public boolean revLazy; // Lazy flag for tree re-rooting (evert)

        public LCTNode(int data) {
            super(data);
        }
    }

    // Homogeneous array of LCTNode objects representing vertices 0..n-1
    protected LCTNode[] nodes;

    public LinkCutTree(int n) {
        super();
        this.nodes = new LCTNode[n];
        for (int i = 0; i < n; i++) {
            this.nodes[i] = new LCTNode(i);
        }
    }
}