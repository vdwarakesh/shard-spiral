# include <algorithm>

// MinHeap is a special type of BinaryHeap where every parent's key is <= its children, stationing the minimum element permanently at heap[0].
class MinHeap : public BinaryHeap {
public:
    MinHeap() : BinaryHeap() {}

    void insert(int val) {
        heap.push_back(val);
        int i = static_cast<int>(heap.size()) - 1;
        // Bubble up while smaller than parent
        while (i > 0 && heap[i] < heap[parent(i)]) {
            std::swap(heap[i], heap[parent(i)]);
            i = parent(i);
        }
    }

    int getMin() const {
        return heap.front();
    }
};