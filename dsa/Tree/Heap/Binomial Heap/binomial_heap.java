// BinomialHeap is a special type of Heap consisting of a collection of Binomial Trees that can be merged in O(log n) time just like binary addition.
public class BinomialHeap extends Heap {
    public static class BinomialNode extends TreeNode {
        public int degree;           // Order k of this Binomial Tree (contains 2^k nodes)
        public BinomialNode parent;
        public BinomialNode child;   // Leftmost child
        public BinomialNode sibling; // Next root or sibling in the list

        public BinomialNode(int key) {
            super(key);
            this.degree = 0;
        }
    }

    protected BinomialNode headRoot; // Linked list of Binomial Tree roots

    public BinomialHeap() {
        super();
        this.headRoot = null;
    }
}