# include <list>

// Base class representing a First-In, First-Out (FIFO) Queue data structure.
class Queue {
protected:
    std::list<int> container; // Doubly linked list supporting O(1) back push and front pop

public:
    virtual ~Queue() = default;

    virtual void enqueue(int value) {
        // Add element to the rear of the queue
        container.push_back(value);
    }

    virtual int dequeue() {
        // Remove and return the oldest element from the front
        int val = container.front();
        container.pop_front();
        return val;
    }

    bool isEmpty() const {
        return container.empty();
    }
};