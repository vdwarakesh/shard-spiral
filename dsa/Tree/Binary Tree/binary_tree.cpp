// BinaryTree is a special type of Tree where every node branches into at most two children: 'left' and 'right'.
class BinaryTree : public Tree {
public:
    struct BinaryNode : public TreeNode {
        BinaryNode* left;   // Pointer to left child
        BinaryNode* right;  // Pointer to right child

        BinaryNode(int val) : TreeNode(val), left(nullptr), right(nullptr) {}
    };

protected:
    BinaryNode* binaryRoot;

public:
    BinaryTree() : Tree(), binaryRoot(nullptr) {}
};