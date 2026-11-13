# include <string>

// Base class representing a String data structure.
// In C++, std::string is a mutable sequence of homogeneous char bytes stored contiguously.
class StringStructure {
protected:
    // Contiguous character buffer storing text data
    std::string sampleText = "Sample string 123";

public:
    size_t length() const {
        return sampleText.length();
    }

    char charAt(size_t index) const {
        return sampleText.at(index);
    }
};