# include <vector>

// DynamicArray is a special type of Array that resizes automatically on demand.
// Inherits from the base Array class.
// Note: In C++ STL, std::vector<T> is the standard built-in Dynamic Array.
class DynamicArray : public Array {
private:
    int* dynamicData;  // Pointer to dynamically allocated contiguous memory
    int size;          // Number of active elements
    int capacity;      // Current allocated capacity

    void resize(int newCapacity) {
        // Allocate a larger block of homogeneous memory (can be any type T)
        int* newData = new int[newCapacity];
        for (int i = 0; i < size; i++) {
            newData[i] = dynamicData[i];
        }
        delete[] dynamicData;
        dynamicData = newData;
        capacity = newCapacity;
    }

public:
    DynamicArray(int initialCapacity = 4) {
        capacity = initialCapacity;
        size = 0;
        dynamicData = new int[capacity];
    }

    ~DynamicArray() {
        delete[] dynamicData;
    }

    void append(int value) {
        if (size == capacity) {
            resize(capacity * 2);
        }
        dynamicData[size++] = value;
    }
};