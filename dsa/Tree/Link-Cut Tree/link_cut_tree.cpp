# include <vector>

// LinkCutTree is a special type of dynamic Tree that maintains preferred paths using auxiliary Splay Trees for O(log n) amortized link, cut, and path aggregate operations.
class LinkCutTree : public Tree {
public:
    struct LCTNode : public TreeNode {
        LCTNode* left = nullptr;
        LCTNode* right = nullptr;
        LCTNode* parent = nullptr; // Splay tree parent or dashed path-parent link
        bool revLazy = false;

        LCTNode(int val = 0) : TreeNode(val) {}
    };

protected:
    std::vector<LCTNode> nodes;

public:
    LinkCutTree(int n) : Tree(), nodes(n) {}

    bool isSplayRoot(const LCTNode* x) const {
        return !x->parent || (x->parent->left != x && x->parent->right != x);
    }
};