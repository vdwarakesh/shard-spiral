// BinarySearchTree is a special type of BinaryTree that keeps keys sorted such that left_subtree < node < right_subtree for every node.
class BinarySearchTree : public BinaryTree {
protected:
    BinaryNode* insertRec(BinaryNode* node, int key) {
        if (node == nullptr) return new BinaryNode(key);
        if (key < node->data) {
            node->left = insertRec(node->left, key);
        } else if (key > node->data) {
            node->right = insertRec(node->right, key);
        }
        return node;
    }

public:
    BinarySearchTree() : BinaryTree() {}

    virtual void insert(int key) {
        binaryRoot = insertRec(binaryRoot, key);
    }
};