// HashMap is a special type of HashTable that maps unique keys to values.
// (In C++ STL, std::unordered_map<K, V> provides a generic HashMap).
class HashMap : public HashTable {
public:
    HashMap(int numBuckets = 16) : HashTable(numBuckets) {}

    void put(int key, int value) {
        int idx = hashKey(key);
        for (auto& pair : buckets[idx]) {
            if (pair.first == key) {
                pair.second = value; // Update existing key's value
                return;
            }
        }
        buckets[idx].emplace_back(key, value);
    }

    int get(int key) const {
        int idx = hashKey(key);
        for (const auto& pair : buckets[idx]) {
            if (pair.first == key) return pair.second;
        }
        return -1; // Not found
    }
};