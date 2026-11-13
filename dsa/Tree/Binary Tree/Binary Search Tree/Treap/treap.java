import java.util.Random;

// Treap is a special type of BinarySearchTree that assigns every node a random heap priority so the tree stays balanced in O(log n) expected height.
public class Treap extends BinarySearchTree {
    private static final Random RAND = new Random();

    public static class TreapNode extends BinaryNode {
        public int priority; // Random heap priority

        public TreapNode(int key) {
            super(key);
            this.priority = RAND.nextInt();
        }
    }

    public Treap() {
        super();
    }
}