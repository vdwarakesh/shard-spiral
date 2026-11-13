// Base class representing an Array data structure.
// In C++, arrays are homogeneous (all elements must share the same data type).
// While we use 'int' here, you can use any primitive type (double, char, bool) or any custom class/data structure (std::string, Tree, std::vector<int>, etc.).
class Array {
protected:
    // Contiguous block of memory storing 5 integers
    int data[5] = {10, 20, 30, 40, 50};
};