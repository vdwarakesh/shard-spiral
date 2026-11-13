// CompressedTrie is a special type of Trie that merges non-branching single-child chains into single edges carrying multi-character substring labels.
public class CompressedTrie extends Trie {
    public static class CompressedNode extends TrieNode {
        public String edgeLabel; // Substring label stored on the incoming edge

        public CompressedNode(String edgeLabel) {
            super();
            this.edgeLabel = edgeLabel;
        }
    }

    public CompressedTrie() {
        super();
        this.trieRoot = new CompressedNode("");
    }
}