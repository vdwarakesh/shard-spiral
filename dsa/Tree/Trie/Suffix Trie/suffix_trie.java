// SuffixTrie is a special type of Trie that indexes all suffixes of a single string so that any substring can be located as a prefix of one of the stored suffixes.
public class SuffixTrie extends Trie {
    public SuffixTrie(String text) {
        super();
        // Insert every suffix starting from index i to the end of the string
        for (int i = 0; i < text.length(); i++) {
            this.insert(text.substring(i));
        }
    }
}