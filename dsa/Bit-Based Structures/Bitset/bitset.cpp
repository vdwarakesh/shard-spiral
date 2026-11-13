# include <vector>

// Bitset is a special type of BitBasedStructures that packs boolean flags into bits, supporting hardware-accelerated 64-at-a-time set operations.
class Bitset : public BitBasedStructures {
private:
    std::vector<unsigned long long> words;
    int numBits;

public:
    Bitset(int size) : numBits(size), words((size + 63) / 64, 0) {}

    void set(int i) {
        words[i / 64] |= (1ULL << (i % 64));
    }

    bool test(int i) const {
        return (words[i / 64] & (1ULL << (i % 64))) != 0;
    }
};