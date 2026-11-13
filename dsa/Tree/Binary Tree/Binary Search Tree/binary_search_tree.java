// BinarySearchTree is a special type of BinaryTree where every node's key is greater than all keys in its left subtree and smaller than all keys in its right subtree.
public class BinarySearchTree extends BinaryTree {
    public BinarySearchTree() {
        super();
    }

    public void insert(int key) {
        this.binaryRoot = insertRec(this.binaryRoot, key);
    }

    protected BinaryNode insertRec(BinaryNode node, int key) {
        if (node == null) {
            return new BinaryNode(key);
        }
        // Step left for smaller values, right for larger values
        if (key < node.data) {
            node.left = insertRec(node.left, key);
        } else if (key > node.data) {
            node.right = insertRec(node.right, key);
        }
        return node;
    }
}