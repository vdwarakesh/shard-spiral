# include <vector>

// BitVector is a special type of Bitset providing O(1) Rank and Select queries via auxiliary superblock directory tables.
class BitVector : public Bitset {
private:
    std::vector<int> rankSuperblocks;

public:
    BitVector(int size) : Bitset(size), rankSuperblocks((size + 511) / 512, 0) {}
};