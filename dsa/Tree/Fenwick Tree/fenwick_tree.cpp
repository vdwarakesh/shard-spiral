# include <vector>

// FenwickTree (Binary Indexed Tree) is a special type of implicit Tree that computes prefix sums and point updates in O(log n) time using only O(n) space.
class FenwickTree : public Tree {
private:
    // 1-indexed array storing power-of-two responsibility ranges
    std::vector<int> bit;
    int n;

public:
    FenwickTree(int size) : Tree(), bit(size + 1, 0), n(size) {}

    void update(int i, int delta) {
        for (; i <= n; i += i & -i) {
            bit[i] += delta;
        }
    }

    int prefixSum(int i) const {
        int sum = 0;
        for (; i > 0; i -= i & -i) {
            sum += bit[i];
        }
        return sum;
    }
};