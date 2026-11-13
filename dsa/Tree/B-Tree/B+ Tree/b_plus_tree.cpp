# include <vector>

// BPlusTree is a special type of BTree in which internal nodes hold only routing keys and all leaf nodes store actual values while linking horizontally via 'nextLeaf'.
class BPlusTree : public BTree {
public:
    struct BPlusNode : public BNode {
        std::vector<int> values; // Data records stored only in leaf nodes
        BPlusNode* nextLeaf;     // Pointer to the next sequential leaf for range scans

        BPlusNode(bool leaf = true) : BNode(leaf), nextLeaf(nullptr) {}
    };

    BPlusTree(int minDegree = 3) : BTree(minDegree) {
        bRoot = new BPlusNode(true);
    }
};