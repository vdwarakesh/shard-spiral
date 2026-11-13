# include <string>

// MutableString is a special type of String backed by a standard std::string that allows direct character overwrites and fast in-place mutations.
class MutableString : public StringStructure {
private:
    std::string buffer; // Editable character buffer

public:
    MutableString(const std::string& initialText) : buffer(initialText) {}

    void setCharAt(size_t index, char ch) {
        buffer[index] = ch; // Direct in-place character assignment
    }

    void append(const std::string& str) {
        buffer.append(str);
    }
};