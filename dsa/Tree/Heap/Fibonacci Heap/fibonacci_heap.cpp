// FibonacciHeap is a special type of Heap that maintains a circular doubly linked root list and uses cascading cuts to achieve O(1) amortized decrease-key and merge.
class FibonacciHeap : public Heap {
public:
    struct FibNode : public TreeNode {
        int degree;
        bool marked;     // Marks whether a child was cut from this node
        FibNode* parent;
        FibNode* child;
        FibNode* left;   // Circular doubly-linked sibling pointers
        FibNode* right;

        FibNode(int val)
            : TreeNode(val), degree(0), marked(false),
              parent(nullptr), child(nullptr), left(this), right(this) {}
    };

protected:
    FibNode* minNode; // Pointer to minimum element in the root ring
    int numNodes;

public:
    FibonacciHeap() : Heap(), minNode(nullptr), numNodes(0) {}
};