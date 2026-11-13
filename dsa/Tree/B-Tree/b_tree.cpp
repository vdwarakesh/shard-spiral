# include <vector>

// BTree is a special type of self-balancing multi-way search Tree designed for block storage, where each node holds up to 2t - 1 sorted keys and 2t children.
class BTree : public Tree {
public:
    struct BNode : public TreeNode {
        std::vector<int> keys;         // Sorted keys in the node (can be templated)
        std::vector<BNode*> bChildren; // Child pointers
        bool isLeaf;

        BNode(bool leaf = true) : TreeNode(0), isLeaf(leaf) {}
    };

protected:
    int t; // Minimum degree (branching factor bound)
    BNode* bRoot;

public:
    BTree(int minDegree = 3) : Tree(), t(minDegree), bRoot(new BNode(true)) {}
};