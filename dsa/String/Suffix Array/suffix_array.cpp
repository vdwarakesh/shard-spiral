# include <vector> include <string> include <numeric> include <algorithm>

// SuffixArray is a special type of String structure that stores sorted suffix indices inside a contiguous integer array.
class SuffixArray {
protected:
    std::vector<int> sa; // Sorted suffix starting positions
    std::string text;

public:
    SuffixArray(const std::string& t) : text(t) {
        int n = text.length();
        sa.resize(n);
        std::iota(sa.begin(), sa.end(), 0);

        // Sort indices based on lexicographical order of their suffixes
        std::sort(sa.begin(), sa.end(), [this](int a, int b) {
            return text.compare(a, std::string::npos, text, b, std::string::npos) < 0;
        });
    }
};