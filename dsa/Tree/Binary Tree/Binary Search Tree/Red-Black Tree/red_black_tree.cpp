// RedBlackTree is a special type of BinarySearchTree that maintains balance via node colors (Red/Black), ensuring uniform black-height and no consecutive red nodes.
class RedBlackTree : public BinarySearchTree {
public:
    enum Color { RED, BLACK };

    struct RBNode : public BinaryNode {
        Color color;      // RED or BLACK bit
        RBNode* parent;   // Upward pointer used during rebalancing fix-ups

        RBNode(int val) : BinaryNode(val), color(RED), parent(nullptr) {}
    };

    RedBlackTree() : BinarySearchTree() {}
};