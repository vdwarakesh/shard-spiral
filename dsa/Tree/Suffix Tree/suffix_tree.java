import java.util.HashMap;
import java.util.Map;

// SuffixTree is a special type of Tree that compresses all suffixes of a string into
// O(n) nodes by labeling edges with (start, end) index bounds into the original text.
public class SuffixTree extends Tree {
    public static class SuffixNode extends TreeNode {
        public int start;                           // Edge substring start index
        public int end;                             // Edge substring end index
        public Map<Character, SuffixNode> children; // Outgoing compressed suffix edges
        public SuffixNode suffixLink;               // Ukkonen suffix link pointer

        public SuffixNode(int start, int end) {
            super(0);
            this.start = start;
            this.end = end;
            this.children = new HashMap<>();
            this.suffixLink = null;
        }
    }

    protected String text;
    protected SuffixNode suffixRoot;

    public SuffixTree(String text) {
        super();
        this.text = text;
        this.suffixRoot = new SuffixNode(-1, -1);
    }
}