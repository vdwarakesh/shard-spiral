// Deque (Double-Ended Queue) is a special type of Queue supporting O(1) insertions and removals at both the front and back ends.
class Deque : public Queue {
public:
    void pushFront(int value) {
        container.push_front(value);
    }

    void pushBack(int value) {
        container.push_back(value);
    }

    int popFront() {
        int val = container.front();
        container.pop_front();
        return val;
    }

    int popBack() {
        int val = container.back();
        container.pop_back();
        return val;
    }
};