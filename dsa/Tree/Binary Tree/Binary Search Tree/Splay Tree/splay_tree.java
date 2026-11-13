// SplayTree is a special type of BinarySearchTree that self-optimizes by rotating
// ("splaying") any searched or inserted node directly to the root for fast repeat access.
public class SplayTree extends BinarySearchTree {
    public SplayTree() {
        super();
    }

    // Zig rotation (Right rotation) used during splaying
    protected BinaryNode rotateRight(BinaryNode x) {
        BinaryNode y = x.left;
        x.left = y.right;
        y.right = x;
        return y;
    }

    // Zag rotation (Left rotation) used during splaying
    protected BinaryNode rotateLeft(BinaryNode x) {
        BinaryNode y = x.right;
        x.right = y.left;
        y.left = x;
        return y;
    }
}