# include <functional>

// Base class for Hash-Based Structures that convert keys into array indices using a deterministic hash function.
class HashBasedStructures {
protected:
    int numBuckets;

    int hashKey(int key) const {
        // Compute bucket index from key using std::hash
        return std::hash<int>{}(key) % numBuckets;
    }

public:
    HashBasedStructures(int buckets = 16) : numBuckets(buckets) {}
    virtual ~HashBasedStructures() = default;
};