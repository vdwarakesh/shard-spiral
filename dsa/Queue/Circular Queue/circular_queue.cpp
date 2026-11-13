# include <vector> include <stdexcept>

// CircularQueue is a special type of Queue (Ring Buffer) that wraps indices around a fixed-capacity array using modulo arithmetic.
class CircularQueue : public Queue {
private:
    std::vector<int> buffer; // Homogeneous fixed-size ring array
    int frontIdx;
    int rearIdx;
    int count;
    int capacity;

public:
    CircularQueue(int cap) : buffer(cap), frontIdx(0), rearIdx(-1), count(0), capacity(cap) {}

    void enqueue(int value) override {
        if (count == capacity) throw std::overflow_error("CircularQueue full");
        rearIdx = (rearIdx + 1) % capacity;
        buffer[rearIdx] = value;
        count++;
    }

    int dequeue() override {
        if (count == 0) throw std::underflow_error("CircularQueue empty");
        int val = buffer[frontIdx];
        frontIdx = (frontIdx + 1) % capacity;
        count--;
        return val;
    }
};