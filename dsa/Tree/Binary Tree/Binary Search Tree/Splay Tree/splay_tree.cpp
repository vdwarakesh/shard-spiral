// SplayTree is a special type of BinarySearchTree that moves accessed nodes to the root via Zig, Zig-Zig, and Zig-Zag rotations without storing extra balance metadata.
class SplayTree : public BinarySearchTree {
protected:
    BinaryNode* rotateRight(BinaryNode* x) {
        BinaryNode* y = x->left;
        x->left = y->right;
        y->right = x;
        return y;
    }

    BinaryNode* rotateLeft(BinaryNode* x) {
        BinaryNode* y = x->right;
        x->right = y->left;
        y->left = x;
        return y;
    }

public:
    SplayTree() : BinarySearchTree() {}
};