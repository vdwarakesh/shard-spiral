# include <vector>

// Base class representing a general hierarchical Tree data structure.
class Tree {
public:
    struct TreeNode {
        int data;                          // Value stored in the node (can be templated)
        std::vector<TreeNode*> children;   // Pointers to child nodes in the hierarchy

        TreeNode(int val) : data(val) {}
    };

protected:
    TreeNode* root; // Topmost node of the tree

public:
    Tree() : root(nullptr) {}
    virtual ~Tree() = default;
};