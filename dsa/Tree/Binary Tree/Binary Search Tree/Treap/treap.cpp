# include <cstdlib>

// Treap is a special type of BinarySearchTree that enforces BST order on keys and Max-Heap order on random priorities to achieve randomized balance.
class Treap : public BinarySearchTree {
public:
    struct TreapNode : public BinaryNode {
        int priority; // Randomly assigned heap priority

        TreapNode(int key) : BinaryNode(key), priority(std::rand()) {}
    };

    Treap() : BinarySearchTree() {}
};