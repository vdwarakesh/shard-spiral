# include <vector>

// A Stack is a linear data structure operating on a Last-In, First-Out (LIFO) policy.
class Stack {
private:
    // Underlying dynamic container (can be templated for any data type)
    std::vector<int> elements;

public:
    void push(int value) {
        // Push element onto the top of the stack in O(1) amortized time
        elements.push_back(value);
    }

    int pop() {
        // Remove and return the top element
        int topVal = elements.back();
        elements.pop_back();
        return topVal;
    }

    int peek() const {
        return elements.back();
    }

    bool isEmpty() const {
        return elements.empty();
    }
};