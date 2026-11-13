import java.util.HashMap;
import java.util.Map;

// EulerTourTree is a special type of dynamic Tree that represents a tree's perimeter
// Euler walk inside a balanced Binary Search Tree for O(log n) subtree queries and cuts.
public class EulerTourTree extends Tree {
    public static class TourNode extends TreeNode {
        public TourNode left, right, parent;
        public int subtreeSize;

        public TourNode(int vertexId) {
            super(vertexId);
            this.subtreeSize = 1;
        }
    }

    // Maps vertex ID to its first and last appearance in the Euler tour sequence
    protected Map<Integer, TourNode> firstVisit = new HashMap<>();
    protected Map<Integer, TourNode> lastVisit = new HashMap<>();

    public EulerTourTree() {
        super();
    }
}