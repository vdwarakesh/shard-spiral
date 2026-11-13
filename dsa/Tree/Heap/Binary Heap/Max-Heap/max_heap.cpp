# include <algorithm>

// MaxHeap is a special type of BinaryHeap where every parent's key is >= its children, stationing the maximum element permanently at heap[0].
class MaxHeap : public BinaryHeap {
public:
    MaxHeap() : BinaryHeap() {}

    void insert(int val) {
        heap.push_back(val);
        int i = static_cast<int>(heap.size()) - 1;
        // Bubble up while larger than parent
        while (i > 0 && heap[i] > heap[parent(i)]) {
            std::swap(heap[i], heap[parent(i)]);
            i = parent(i);
        }
    }

    int getMax() const {
        return heap.front();
    }
};