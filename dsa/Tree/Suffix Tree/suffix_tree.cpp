# include <unordered_map> include <string>

// SuffixTree is a special type of Tree that represents all suffixes of a text in O(n) space using compressed (start, end) index edges and suffix links.
class SuffixTree : public Tree {
public:
    struct SuffixNode : public TreeNode {
        int start;
        int end;
        std::unordered_map<char, SuffixNode*> suffixChildren;
        SuffixNode* suffixLink;

        SuffixNode(int s = -1, int e = -1)
            : TreeNode(0), start(s), end(e), suffixLink(nullptr) {}
    };

protected:
    std::string text;
    SuffixNode* suffixRoot;

public:
    SuffixTree(const std::string& t = "")
        : Tree(), text(t), suffixRoot(new SuffixNode()) {}
};