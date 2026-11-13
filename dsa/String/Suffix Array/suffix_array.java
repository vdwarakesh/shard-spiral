import java.util.Arrays;

// SuffixArray is a special type of String structure storing sorted suffix start indices for efficient substring searching without heavy pointer trees.
public class SuffixArray {
    // Homogeneous array storing sorted starting indices of all suffixes
    protected int[] sa;
    protected String text;

    public SuffixArray(String text) {
        this.text = text;
        int n = text.length();
        Integer[] indices = new Integer[n];
        for (int i = 0; i < n; i++) indices[i] = i;

        // Sort suffix substrings lexicographically
        Arrays.sort(indices, (a, b) -> text.substring(a).compareTo(text.substring(b)));

        this.sa = new int[n];
        for (int i = 0; i < n; i++) {
            this.sa[i] = indices[i];
        }
    }
}