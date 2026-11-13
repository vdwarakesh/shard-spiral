// TopTree is a special type of hierarchical dynamic Tree that recursively contracts tree clusters via Compress (path) and Rake (subtree) merges for O(log n) path + subtree queries.
public class TopTree extends Tree {
    public enum ClusterType { BASE_EDGE, COMPRESS, RAKE }

    public static class ClusterNode extends TreeNode {
        public ClusterType type;
        public int boundaryU;          // First boundary vertex of the cluster
        public int boundaryV;          // Second boundary vertex of the cluster
        public ClusterNode leftChild;  // First sub-cluster
        public ClusterNode rightChild; // Second sub-cluster

        public ClusterNode(ClusterType type, int u, int v) {
            super(0);
            this.type = type;
            this.boundaryU = u;
            this.boundaryV = v;
        }
    }

    protected ClusterNode topRoot;

    public TopTree() {
        super();
    }
}