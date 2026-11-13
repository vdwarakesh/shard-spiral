// MutableString (comparable to java.lang.StringBuilder) is a special type of String that permits direct in-place modifications and fast appends without object allocations.
public class MutableString extends StringStructure {
    // Underlying dynamic character buffer
    private StringBuilder buffer;

    public MutableString(String initialText) {
        this.buffer = new StringBuilder(initialText);
    }

    public void setCharAt(int index, char ch) {
        // Mutate character directly in place
        this.buffer.setCharAt(index, ch);
    }

    public void append(String str) {
        this.buffer.append(str);
    }
}