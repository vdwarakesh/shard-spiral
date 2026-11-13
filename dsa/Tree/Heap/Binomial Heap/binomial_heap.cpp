// BinomialHeap is a special type of Heap storing a forest of Binomial Trees where at most one tree of each degree k (size 2^k) exists, supporting O(log n) melding.
class BinomialHeap : public Heap {
public:
    struct BinomialNode : public TreeNode {
        int degree;            // Order k of the binomial tree
        BinomialNode* parent;
        BinomialNode* child;   // Leftmost child pointer
        BinomialNode* sibling; // Right sibling pointer

        BinomialNode(int val)
            : TreeNode(val), degree(0), parent(nullptr), child(nullptr), sibling(nullptr) {}
    };

protected:
    BinomialNode* headRoot;

public:
    BinomialHeap() : Heap(), headRoot(nullptr) {}
};