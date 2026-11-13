// AVLTree is a special type of BinarySearchTree that automatically balances itself using rotations so no node's left and right subtree heights differ by more than 1.
public class AVLTree extends BinarySearchTree {
    public static class AVLNode extends BinaryNode {
        public int height; // Height of this node's subtree

        public AVLNode(int data) {
            super(data);
            this.height = 1;
        }
    }

    protected int height(AVLNode node) {
        return (node == null) ? 0 : node.height;
    }

    protected int getBalanceFactor(AVLNode node) {
        // Difference between left and right subtree heights
        return (node == null) ? 0 : height((AVLNode) node.left) - height((AVLNode) node.right);
    }

    protected AVLNode rotateRight(AVLNode y) {
        // Local pointer rotation to restore O(log n) height balance
        AVLNode x = (AVLNode) y.left;
        BinaryNode t2 = x.right;
        x.right = y;
        y.left = t2;
        y.height = Math.max(height((AVLNode) y.left), height((AVLNode) y.right)) + 1;
        x.height = Math.max(height((AVLNode) x.left), height((AVLNode) x.right)) + 1;
        return x;
    }
}