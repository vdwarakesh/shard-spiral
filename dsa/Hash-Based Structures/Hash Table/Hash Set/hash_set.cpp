// HashSet is a special type of HashTable that stores unique keys and answers membership queries ("is X in the set?") in O(1) average time.
class HashSet : public HashTable {
public:
    HashSet(int numBuckets = 16) : HashTable(numBuckets) {}

    void add(int key) {
        if (!contains(key)) {
            buckets[hashKey(key)].emplace_back(key, 1);
        }
    }

    bool contains(int key) const {
        int idx = hashKey(key);
        for (const auto& pair : buckets[idx]) {
            if (pair.first == key) return true;
        }
        return false;
    }
};