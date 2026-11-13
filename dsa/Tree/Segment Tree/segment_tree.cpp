# include <vector>

// SegmentTree is a special type of BinaryTree that stores interval aggregates over an array for O(log n) range queries and updates.
class SegmentTree : public BinaryTree {
protected:
    // Homogeneous vector storing segment aggregates (can be templated for any type)
    std::vector<int> segTree;
    int n;

    void build(const std::vector<int>& arr, int node, int start, int end) {
        if (start == end) {
            segTree[node] = arr[start];
            return;
        }
        int mid = start + (end - start) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        segTree[node] = segTree[2 * node] + segTree[2 * node + 1];
    }

public:
    SegmentTree(const std::vector<int>& arr = {}) : BinaryTree(), n(arr.size()) {
        segTree.assign(4 * n, 0);
        if (n > 0) build(arr, 1, 0, n - 1);
    }
};