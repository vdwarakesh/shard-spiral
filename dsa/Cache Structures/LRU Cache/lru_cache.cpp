# include <unordered_map> include <list> include <utility>

// LRUCache is a special type of CacheStructures combining a hash map and a doubly linked list for O(1) LRU get, put, and eviction operations.
class LRUCache : public CacheStructures {
private:
    std::list<std::pair<int, int>> itemList; // Doubly linked list of (key, value)
    std::unordered_map<int, std::list<std::pair<int, int>>::iterator> cacheMap;

public:
    LRUCache(int cap) : CacheStructures(cap) {}

    int get(int key) {
        auto it = cacheMap.find(key);
        if (it == cacheMap.end()) return -1;
        itemList.splice(itemList.begin(), itemList, it->second); // Move to front
        return it->second->second;
    }

    void put(int key, int value) {
        auto it = cacheMap.find(key);
        if (it != cacheMap.end()) {
            itemList.splice(itemList.begin(), itemList, it->second);
            it->second->second = value;
            return;
        }
        if (itemList.size() >= static_cast<size_t>(capacity)) {
            int lruKey = itemList.back().first;
            itemList.pop_back();
            cacheMap.erase(lruKey);
        }
        itemList.emplace_front(key, value);
        cacheMap[key] = itemList.begin();
    }
};