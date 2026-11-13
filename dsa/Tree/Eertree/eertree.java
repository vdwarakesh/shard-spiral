import java.util.HashMap;
import java.util.Map;

// Eertree (Palindromic Tree) is a special type of dual-rooted Tree structure where every node represents a distinct palindromic substring of a text in O(n) space.
public class Eertree extends Tree {
    public static class PalindromeNode extends TreeNode {
        public int length;                              // Length of the palindrome
        public Map<Character, PalindromeNode> edges;    // Transitions P -> xPx
        public PalindromeNode suffixLink;               // Longest proper palindromic suffix

        public PalindromeNode(int length) {
            super(length);
            this.length = length;
            this.edges = new HashMap<>();
        }
    }

    protected PalindromeNode oddRoot;  // Root of length -1
    protected PalindromeNode evenRoot; // Root of length 0

    public Eertree() {
        super();
        this.oddRoot = new PalindromeNode(-1);
        this.oddRoot.suffixLink = this.oddRoot;
        this.evenRoot = new PalindromeNode(0);
        this.evenRoot.suffixLink = this.oddRoot;
    }
}