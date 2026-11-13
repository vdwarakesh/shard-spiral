// DynamicSegmentTree is a special type of SegmentTree that allocates child nodes on the fly only when visited, supporting huge coordinate bounds [0, 10^18].
class DynamicSegmentTree : public SegmentTree {
private:
    long long minCoord;
    long long maxCoord;

public:
    DynamicSegmentTree(long long minC = 0, long long maxC = 1000000000LL)
        : SegmentTree(), minCoord(minC), maxCoord(maxC) {
        binaryRoot = new BinaryNode(0);
    }

    void update(BinaryNode* node, long long start, long long end, long long idx, int val) {
        if (start == end) {
            node->data += val;
            return;
        }
        long long mid = start + (end - start) / 2;
        if (idx <= mid) {
            if (!node->left) node->left = new BinaryNode(0);
            update(node->left, start, mid, idx, val);
        } else {
            if (!node->right) node->right = new BinaryNode(0);
            update(node->right, mid + 1, end, idx, val);
        }
        node->data = (node->left ? node->left->data : 0) +
                     (node->right ? node->right->data : 0);
    }
};