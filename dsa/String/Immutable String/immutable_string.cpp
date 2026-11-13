# include <string>

// ImmutableString is a special type of String wrapped to prevent in-place modifications, guaranteeing thread safety and safe hash caching.
class ImmutableString : public StringStructure {
private:
    const std::string text; // Read-only member variable

public:
    ImmutableString(const std::string& t) : text(t) {}

    const std::string& getText() const {
        return text;
    }
};