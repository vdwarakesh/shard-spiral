// Base class representing a String data structure.
// In Java, java.lang.String is a homogeneous, immutable sequence of 16-bit char units.
public class StringStructure {
    // Immutable character sequence stored in contiguous memory or byte array under the hood
    protected String sampleText = "Sample string 123";

    public int length() {
        return sampleText.length();
    }

    public char charAt(int index) {
        return sampleText.charAt(index);
    }
}