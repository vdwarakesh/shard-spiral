# include <algorithm>

// AVLTree is a special type of BinarySearchTree that maintains strict O(log n) height balance by ensuring every node has a balance factor in {-1, 0, 1}.
class AVLTree : public BinarySearchTree {
public:
    struct AVLNode : public BinaryNode {
        int height; // Subtree height stored for O(1) balance checks
        AVLNode(int val) : BinaryNode(val), height(1) {}
    };

protected:
    int getHeight(AVLNode* n) const {
        return n ? n->height : 0;
    }

    int getBalanceFactor(AVLNode* n) const {
        return n ? getHeight(static_cast<AVLNode*>(n->left)) -
                   getHeight(static_cast<AVLNode*>(n->right)) : 0;
    }

    AVLNode* rotateRight(AVLNode* y) {
        AVLNode* x = static_cast<AVLNode*>(y->left);
        BinaryNode* T2 = x->right;
        x->right = y;
        y->left = T2;
        y->height = 1 + std::max(getHeight(static_cast<AVLNode*>(y->left)),
                                 getHeight(static_cast<AVLNode*>(y->right)));
        x->height = 1 + std::max(getHeight(static_cast<AVLNode*>(x->left)),
                                 getHeight(static_cast<AVLNode*>(x->right)));
        return x;
    }
};