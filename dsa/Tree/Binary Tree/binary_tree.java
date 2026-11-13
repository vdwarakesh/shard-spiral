// BinaryTree is a special type of Tree where every node is restricted to at most two children: a left child and a right child.
public class BinaryTree extends Tree {
    public static class BinaryNode extends TreeNode {
        public BinaryNode left;  // Left branch child
        public BinaryNode right; // Right branch child

        public BinaryNode(int data) {
            super(data);
            this.left = null;
            this.right = null;
        }
    }

    protected BinaryNode binaryRoot;

    public BinaryTree() {
        super();
        this.binaryRoot = null;
    }
}