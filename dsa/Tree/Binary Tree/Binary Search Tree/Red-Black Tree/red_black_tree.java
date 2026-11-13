// RedBlackTree is a special type of BinarySearchTree that uses a single color bit
// (Red or Black) per node plus rotations to keep the tree balanced in O(log n) height.
public class RedBlackTree extends BinarySearchTree {
    public static final boolean RED = true;
    public static final boolean BLACK = false;

    public static class RBNode extends BinaryNode {
        public boolean color;  // Node color (RED or BLACK)
        public RBNode parent;  // Reference to parent for fix-up rotations

        public RBNode(int data) {
            super(data);
            this.color = RED; // Newly inserted nodes start out RED
            this.parent = null;
        }
    }

    public RedBlackTree() {
        super();
    }
}