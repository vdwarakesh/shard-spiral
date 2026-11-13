// TwoThreeTree (2-3 Tree) is a special type of BTree with max degree 3 where every internal node is a 2-node (1 key, 2 children) or 3-node (2 keys, 3 children).
class TwoThreeTree : public BTree {
public:
    static const int MAX_KEYS = 2;
    static const int MAX_DEGREE = 3;

    TwoThreeTree() : BTree(2) {}
};