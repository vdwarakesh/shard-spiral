# include <string>

// SuffixTrie is a special type of Trie that inserts every suffix of a text into the character trie for O(m) pattern matching.
class SuffixTrie : public Trie {
public:
    SuffixTrie(const std::string& text = "") : Trie() {
        // Populate the trie with all suffixes text[i..n-1]
        for (size_t i = 0; i < text.length(); i++) {
            insert(text.substr(i));
        }
    }
};