# include <unordered_map> include <string>

// Trie is a special type of Tree that branches by individual characters to store strings with shared prefixes along common paths from the root.
class Trie : public Tree {
public:
    struct TrieNode : public TreeNode {
        std::unordered_map<char, TrieNode*> charChildren;
        bool isEndOfWord;

        TrieNode() : TreeNode(0), isEndOfWord(false) {}
    };

protected:
    TrieNode* trieRoot;

public:
    Trie() : Tree(), trieRoot(new TrieNode()) {}

    void insert(const std::string& word) {
        TrieNode* curr = trieRoot;
        for (char ch : word) {
            if (curr->charChildren.find(ch) == curr->charChildren.end()) {
                curr->charChildren[ch] = new TrieNode();
            }
            curr = curr->charChildren[ch];
        }
        curr->isEndOfWord = true;
    }
};