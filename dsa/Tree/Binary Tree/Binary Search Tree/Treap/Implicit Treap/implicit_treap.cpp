// ImplicitTreap is a special type of Treap that tracks subtree sizes to use a node's in-order index as an implicit key, acting like a cut-and-paste dynamic array.
class ImplicitTreap : public Treap {
public:
    struct ImplicitNode : public TreapNode {
        int subtreeSize; // Used to compute implicit array index = size(left)

        ImplicitNode(int val) : TreapNode(val), subtreeSize(1) {}
    };

    int getSize(ImplicitNode* n) const {
        return n ? n->subtreeSize : 0;
    }

    void updateSize(ImplicitNode* n) {
        if (n) {
            n->subtreeSize = 1 + getSize(static_cast<ImplicitNode*>(n->left))
                               + getSize(static_cast<ImplicitNode*>(n->right));
        }
    }
};