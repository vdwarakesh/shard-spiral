# include <vector>

// BinaryHeap is a special type of Heap that uses a Complete Binary Tree layout stored inside a contiguous array (std::vector).
class BinaryHeap : public Heap {
protected:
    // Homogeneous contiguous array; can be templated for any data type
    std::vector<int> heap;

    int parent(int i) const { return (i - 1) / 2; }
    int leftChild(int i) const { return 2 * i + 1; }
    int rightChild(int i) const { return 2 * i + 2; }

public:
    BinaryHeap() : Heap() {}
};