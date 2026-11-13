// XORTrie is a special type of Trie that branches on binary bits (0 and 1) from MSB to LSB to solve bitwise XOR optimization problems in O(log(MAX_VAL)) time.
class XORTrie : public Trie {
public:
    struct XORNode : public TrieNode {
        // Homogeneous array of 2 pointers: 0-branch and 1-branch
        XORNode* bitChildren[2] = {nullptr, nullptr};
    };

private:
    XORNode* xorRoot;
    int maxBits;

public:
    XORTrie(int bits = 32) : Trie(), xorRoot(new XORNode()), maxBits(bits) {}

    void insertNumber(int num) {
        XORNode* curr = xorRoot;
        for (int b = maxBits - 1; b >= 0; b--) {
            int bit = (num >> b) & 1;
            if (!curr->bitChildren[bit]) {
                curr->bitChildren[bit] = new XORNode();
            }
            curr = curr->bitChildren[bit];
        }
    }
};