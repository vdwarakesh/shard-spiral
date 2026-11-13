// XORTrie is a special type of Trie that stores integers bit by bit (0 or 1) from most significant bit to least significant bit for fast bitwise XOR queries.
public class XORTrie extends Trie {
    public static class XORNode extends TrieNode {
        // Homogeneous array of 2 child nodes: child[0] for bit 0, child[1] for bit 1
        public XORNode[] bitChildren = new XORNode[2];
    }

    private final int maxBits;
    private final XORNode xorRoot;

    public XORTrie(int maxBits) {
        super();
        this.maxBits = maxBits;
        this.xorRoot = new XORNode();
    }

    public void insertNumber(int num) {
        XORNode curr = this.xorRoot;
        for (int b = this.maxBits - 1; b >= 0; b--) {
            int bit = (num >> b) & 1;
            if (curr.bitChildren[bit] == null) {
                curr.bitChildren[bit] = new XORNode();
            }
            curr = curr.bitChildren[bit];
        }
    }
}