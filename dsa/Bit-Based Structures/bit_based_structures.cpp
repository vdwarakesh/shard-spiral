// Base class for Bit-Based Structures manipulating individual bits inside CPU words.
class BitBasedStructures {
protected:
    unsigned long long bitWord; // 64-bit word packing 64 binary flags

public:
    BitBasedStructures() : bitWord(0) {}
    virtual ~BitBasedStructures() = default;
};