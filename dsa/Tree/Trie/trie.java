import java.util.HashMap;
import java.util.Map;

// Trie (Prefix Tree) is a special type of Tree that indexes strings character by character along branches so words sharing a prefix share the same root path.
public class Trie extends Tree {
    public static class TrieNode extends TreeNode {
        public Map<Character, TrieNode> charChildren; // Maps next character to child node
        public boolean isEndOfWord;                   // Marks complete words

        public TrieNode() {
            super(0);
            this.charChildren = new HashMap<>();
            this.isEndOfWord = false;
        }
    }

    protected TrieNode trieRoot;

    public Trie() {
        super();
        this.trieRoot = new TrieNode();
    }

    public void insert(String word) {
        TrieNode curr = this.trieRoot;
        for (char ch : word.toCharArray()) {
            curr.charChildren.putIfAbsent(ch, new TrieNode());
            curr = curr.charChildren.get(ch);
        }
        curr.isEndOfWord = true;
    }
}