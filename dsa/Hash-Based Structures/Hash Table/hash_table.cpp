# include <vector> include <list> include <utility>

// HashTable is a special type of HashBasedStructures that manages an array of buckets and resolves collisions via separate chaining.
class HashTable : public HashBasedStructures {
protected:
    // Array (vector) of doubly-linked lists storing (key, value) pairs per bucket
    std::vector<std::list<std::pair<int, int>>> buckets;

public:
    HashTable(int numBuckets = 16)
        : HashBasedStructures(numBuckets), buckets(numBuckets) {}
};