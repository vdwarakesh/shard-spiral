// FibonacciHeap is a special type of Heap that lazily defers tree consolidation until
// Extract-Min, achieving O(1) amortized time for insertions, merges, and decrease-key.
public class FibonacciHeap extends Heap {
    public static class FibNode extends TreeNode {
        public int degree;
        public boolean marked; // True if node lost a child since becoming a child itself
        public FibNode parent;
        public FibNode child;
        public FibNode left;   // Circular doubly linked list neighbor
        public FibNode right;

        public FibNode(int key) {
            super(key);
            this.degree = 0;
            this.marked = false;
            this.left = this;
            this.right = this;
        }
    }

    protected FibNode minNode; // Points directly to the minimum root node
    protected int count;

    public FibonacciHeap() {
        super();
        this.minNode = null;
        this.count = 0;
    }
}