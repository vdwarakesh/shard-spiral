// TwoThreeFourTree (2-3-4 Tree) is a special type of BTree (t = 2, max degree = 4) where nodes hold 1 to 3 keys and 2 to 4 children; isomorphic to a Red-Black Tree.
class TwoThreeFourTree : public BTree {
public:
    static const int MAX_KEYS = 3;
    static const int MAX_DEGREE = 4;

    TwoThreeFourTree() : BTree(2) {}
};