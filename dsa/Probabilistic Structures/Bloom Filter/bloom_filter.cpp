# include <vector> include <cmath> include <functional>

// BloomFilter is a special type of ProbabilisticStructures utilizing a bit array and k hash functions to test set membership in compact space.
class BloomFilter : public ProbabilisticStructures {
private:
    std::vector<bool> bitArray;
    int m;
    int k;

public:
    BloomFilter(int capacity, double fpRate = 0.01) : ProbabilisticStructures(fpRate) {
        m = static_cast<int>(-capacity * std::log(fpRate) / (std::log(2) * std::log(2)));
        k = std::max(1, static_cast<int>((static_cast<double>(m) / capacity) * std::log(2)));
        bitArray.assign(m, false);
    }
};