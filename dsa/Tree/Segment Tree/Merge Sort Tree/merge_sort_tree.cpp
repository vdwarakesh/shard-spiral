# include <vector> include <algorithm>

// MergeSortTree is a special type of SegmentTree where each node stores a sorted std::vector of all elements in its segment to answer range threshold queries.
class MergeSortTree : public SegmentTree {
protected:
    std::vector<std::vector<int>> sortedTree;

    void buildSorted(const std::vector<int>& arr, int node, int start, int end) {
        if (start == end) {
            sortedTree[node] = {arr[start]};
            return;
        }
        int mid = start + (end - start) / 2;
        buildSorted(arr, 2 * node, start, mid);
        buildSorted(arr, 2 * node + 1, mid + 1, end);
        // Merge sorted left and right child vectors in O(len) time
        sortedTree[node].resize(sortedTree[2 * node].size() + sortedTree[2 * node + 1].size());
        std::merge(sortedTree[2 * node].begin(), sortedTree[2 * node].end(),
                   sortedTree[2 * node + 1].begin(), sortedTree[2 * node + 1].end(),
                   sortedTree[node].begin());
    }

public:
    MergeSortTree(const std::vector<int>& arr) : SegmentTree(), sortedTree(4 * arr.size()) {
        n = arr.size();
        if (n > 0) buildSorted(arr, 1, 0, n - 1);
    }
};