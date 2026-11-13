# include <vector>

// PersistentSegmentTree is a special type of SegmentTree that preserves all past versions using path copying (O(log n) new nodes per update) and structural sharing.
class PersistentSegmentTree : public SegmentTree {
public:
    struct PersistentNode : public BinaryNode {
        PersistentNode(int sum = 0, BinaryNode* l = nullptr, BinaryNode* r = nullptr)
            : BinaryNode(sum) {
            left = l;
            right = r;
        }
    };

protected:
    // Array of version roots; versionRoots[v] is the tree after update v
    std::vector<PersistentNode*> versionRoots;

public:
    PersistentSegmentTree(int size) : SegmentTree() {
        n = size;
    }
};