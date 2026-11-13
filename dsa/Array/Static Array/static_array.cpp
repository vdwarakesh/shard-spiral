# include <array>

// StaticArray is a special type of Array whose size is fixed at compile time.
// Inherits from the base Array class.
class StaticArray : public Array {
public:
    // C++ std::array wraps a fixed-size C-style static array.
    // Homogeneous container: uses 'int' here, but can hold any data type or structure.
    std::array<int, 5> fixedData = {10, 20, 30, 40, 50};

    void set(int index, int value) {
        // O(1) direct index assignment within fixed bounds
        fixedData[index] = value;
    }

    int get(int index) const {
        return fixedData[index];
    }
};