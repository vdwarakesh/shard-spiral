// OrderStatisticTree is a special type of BinarySearchTree that augments each node with a subtree node count ('size') for O(log n) rank and k-th element queries.
class OrderStatisticTree : public BinarySearchTree {
public:
    struct OSNode : public BinaryNode {
        int size; // Subtree size = left->size + right->size + 1

        OSNode(int key) : BinaryNode(key), size(1) {}
    };

    int getSize(OSNode* n) const {
        return n ? n->size : 0;
    }
};