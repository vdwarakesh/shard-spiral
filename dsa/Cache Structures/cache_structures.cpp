// Base class for Cache Structures managing bounded-capacity fast memory.
class CacheStructures {
protected:
    int capacity;

public:
    CacheStructures(int cap) : capacity(cap) {}
    virtual ~CacheStructures() = default;
};