// ImmutableString is a special type of String (like standard java.lang.String) where contents are permanently write-protected after creation.
public class ImmutableString extends StringStructure {
    private final String text;

    public ImmutableString(String text) {
        this.text = text; // Final reference cannot be reassigned; chars cannot be edited
    }

    public String getText() {
        return this.text;
    }
}