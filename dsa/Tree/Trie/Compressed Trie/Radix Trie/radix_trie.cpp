# include <unordered_map> include <string>

// RadixTrie is a special type of CompressedTrie that stores multi-character prefix chunks per node and branches only where keys diverge.
class RadixTrie : public CompressedTrie {
public:
    struct RadixNode : public CompressedNode {
        std::unordered_map<char, RadixNode*> edges;

        RadixNode(const std::string& prefix = "") : CompressedNode(prefix) {}
    };

    RadixTrie() : CompressedTrie() {}
};