# include <vector> include <algorithm> include <cmath>

// SparseTable precomputes power-of-two interval blocks over a static array, allowing O(1) constant-time queries for operations like Range Minimum.
class SparseTable {
protected:
    // 2D homogeneous vector representing the table
    std::vector<std::vector<int>> st;
    std::vector<int> logTable;
    int n;

public:
    SparseTable(const std::vector<int>& arr) : n(arr.size()) {
        if (n == 0) return;
        
        int maxK = std::log2(n) + 1;
        st.assign(maxK, std::vector<int>(n));
        logTable.assign(n + 1, 0);

        // Precalculate floor of log2 for instant queries
        for (int i = 2; i <= n; i++) {
            logTable[i] = logTable[i / 2] + 1;
        }

        for (int i = 0; i < n; i++) {
            st[0][i] = arr[i];
        }

        // Merge smaller power-of-two intervals into larger ones
        for (int k = 1; k < maxK; k++) {
            for (int i = 0; i + (1 << k) <= n; i++) {
                st[k][i] = std::min(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
            }
        }
    }

    int queryMin(int left, int right) const {
        int k = logTable[right - left + 1];
        // O(1) minimum of two overlapping precalculated blocks
        return std::min(st[k][left], st[k][right - (1 << k) + 1]);
    }
};