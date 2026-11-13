// Heap is a special type of Tree in which every parent node satisfies a priority ordering invariant relative to its children.
class Heap : public Tree {
public:
    Heap() : Tree() {}
    virtual ~Heap() = default;
};