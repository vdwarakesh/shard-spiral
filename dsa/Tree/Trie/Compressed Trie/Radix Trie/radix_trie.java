import java.util.HashMap;
import java.util.Map;

// RadixTrie is a special type of CompressedTrie that branches on fixed-radix chunks while storing multi-character prefix segments along compressed edges.
public class RadixTrie extends CompressedTrie {
    public static class RadixNode extends CompressedNode {
        public Map<Character, RadixNode> edges; // Keyed by starting character of the edge

        public RadixNode(String prefix) {
            super(prefix);
            this.edges = new HashMap<>();
        }
    }

    public RadixTrie() {
        super();
        this.trieRoot = new RadixNode("");
    }
}