# include <vector> include <string>

// CountingBloomFilter is a special type of BloomFilter storing multi-bit tally counters to allow item deletions.
class CountingBloomFilter : public BloomFilter {
private:
    std::vector<int> counters;

public:
    CountingBloomFilter(int capacity, double fpRate = 0.01) : BloomFilter(capacity, fpRate) {
        counters.assign(m, 0);
    }

    void remove(const std::string& item) {
        for (int seed = 0; seed < k; seed++) {
            int idx = std::hash<std::string>{}(item + std::to_string(seed)) % m;
            if (counters[idx] > 0) counters[idx]--;
        }
    }
};