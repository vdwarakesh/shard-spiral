import java.util.ArrayList;
import java.util.List;

// Base class representing a general hierarchical Tree data structure.
public class Tree {
    // Node building block for a general multi-way tree
    public static class TreeNode {
        public int data; // Can hold any primitive or Object data type
        public List<TreeNode> children; // List of child nodes branching from this node

        public TreeNode(int data) {
            this.data = data;
            this.children = new ArrayList<>();
        }

        public void addChild(TreeNode child) {
            this.children.add(child);
        }
    }

    protected TreeNode root; // Topmost starting node of the tree

    public Tree() {
        this.root = null;
    }
}