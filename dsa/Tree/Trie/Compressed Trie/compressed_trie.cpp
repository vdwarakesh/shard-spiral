# include <string>

// CompressedTrie is a special type of Trie that contracts one-child node chains into single edges labeled with multi-character substrings.
class CompressedTrie : public Trie {
public:
    struct CompressedNode : public TrieNode {
        std::string edgeLabel; // Compressed multi-character prefix on the incoming edge

        CompressedNode(const std::string& label = "")
            : TrieNode(), edgeLabel(label) {}
    };

    CompressedTrie() : Trie() {}
};