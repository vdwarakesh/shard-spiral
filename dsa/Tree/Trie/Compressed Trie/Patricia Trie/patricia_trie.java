// PatriciaTrie is a special type of CompressedTrie that operates at the binary bit level
// (radix = 2), storing the critical bit index where keys diverge at each internal node.
public class PatriciaTrie extends CompressedTrie {
    public static class PatriciaNode extends CompressedNode {
        public int bitIndex;       // Exact bit position to inspect next
        public String key;         // Full key stored for final equality verification
        public PatriciaNode left;  // Branch taken when bit at bitIndex is 0
        public PatriciaNode right; // Branch taken when bit at bitIndex is 1

        public PatriciaNode(int bitIndex, String key) {
            super("");
            this.bitIndex = bitIndex;
            this.key = key;
        }
    }

    public PatriciaTrie() {
        super();
    }
}