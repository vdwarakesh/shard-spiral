# include <queue> include <vector>

// PriorityQueue is a special type of Queue that always serves the element with the highest priority first, backed under the hood by a Binary Heap.
class PriorityQueue : public Queue {
private:
    std::priority_queue<int> maxHeap;

public:
    void enqueue(int value) override {
        // Inserts element in O(log n) time ordered by priority
        maxHeap.push(value);
    }

    int dequeue() override {
        // Removes and returns the highest-priority element in O(log n) time
        int topVal = maxHeap.top();
        maxHeap.pop();
        return topVal;
    }
};