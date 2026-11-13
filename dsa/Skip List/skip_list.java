import java.util.Random;

// SkipList is a special type of randomized multi-level linked list providing
// O(log n) search and insert speeds without tree balancing rotations.
public class SkipList {
    public static class SkipNode {
        public int val;
        // Homogeneous array of forward pointers across stacked express lanes
        public SkipNode[] forward;

        public SkipNode(int val, int level) {
            this.val = val;
            this.forward = new SkipNode[level + 1];
        }
    }

    protected SkipNode head;
    protected int maxLevel;
    protected int currentLevel;
    protected Random rand;

    public SkipList(int maxLevel) {
        this.maxLevel = maxLevel;
        this.currentLevel = 0;
        this.head = new SkipNode(Integer.MIN_VALUE, maxLevel);
        this.rand = new Random();
    }
}