# include <string>

// PatriciaTrie is a special type of CompressedTrie (binary radix-2 trie) that stores only the critical bit index where keys diverge, eliminating one-way branches.
class PatriciaTrie : public CompressedTrie {
public:
    struct PatriciaNode : public CompressedNode {
        int bitIndex;        // Critical bit position where keys branch
        std::string key;     // Full key stored at leaf for single final comparison
        PatriciaNode* left;  // Bit 0 branch
        PatriciaNode* right; // Bit 1 branch

        PatriciaNode(int bit = -1, const std::string& k = "")
            : CompressedNode(""), bitIndex(bit), key(k), left(nullptr), right(nullptr) {}
    };

    PatriciaTrie() : CompressedTrie() {}
};