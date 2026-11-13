# include <unordered_map>

// Eertree (Palindromic Tree) is a special type of Tree with two roots (lengths -1 and 0) that indexes every distinct palindrome of a string in linear O(n) space and time.
class Eertree : public Tree {
public:
    struct PalindromeNode : public TreeNode {
        int length;
        std::unordered_map<char, PalindromeNode*> edges; // Edge 'x' wraps P into xPx
        PalindromeNode* suffixLink;

        PalindromeNode(int len) : TreeNode(len), length(len), suffixLink(nullptr) {}
    };

protected:
    PalindromeNode* oddRoot;  // Length -1 root
    PalindromeNode* evenRoot; // Length 0 root

public:
    Eertree() : Tree() {
        oddRoot = new PalindromeNode(-1);
        oddRoot->suffixLink = oddRoot;
        evenRoot = new PalindromeNode(0);
        evenRoot->suffixLink = oddRoot;
    }
};