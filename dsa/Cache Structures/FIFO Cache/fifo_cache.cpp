# include <unordered_map> include <queue> include <utility>

// FIFOCache is a special type of CacheStructures evicting items in FIFO arrival order.
class FIFOCache : public CacheStructures {
private:
    std::unordered_map<int, int> cacheMap;
    std::queue<int> insertionQueue;

public:
    FIFOCache(int cap) : CacheStructures(cap) {}

    void put(int key, int value) {
        if (cacheMap.find(key) == cacheMap.end()) {
            if (cacheMap.size() >= static_cast<size_t>(capacity)) {
                int oldestKey = insertionQueue.front();
                insertionQueue.pop();
                cacheMap.erase(oldestKey);
            }
            insertionQueue.push(key);
        }
        cacheMap[key] = value;
    }
};