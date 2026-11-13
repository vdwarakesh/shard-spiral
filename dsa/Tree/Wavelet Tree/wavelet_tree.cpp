# include <vector>

// WaveletTree is a special type of BinaryTree that partitions sequences by value alphabet using bitvector rank tables at each node for O(log Sigma) range quantile queries.
class WaveletTree : public BinaryTree {
public:
    struct WaveletNode : public BinaryNode {
        int lowVal;
        int highVal;
        std::vector<int> prefixZeros; // Rank_0 table mapping parent ranges to child ranges

        WaveletNode(int low, int high) : BinaryNode(0), lowVal(low), highVal(high) {}
    };

    WaveletTree() : BinaryTree() {}
};