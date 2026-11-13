# include <unordered_map> include <list> include <utility>

// MRUCache is a special type of CacheStructures that evicts the most recently accessed item to optimize sequential full-table scans.
class MRUCache : public CacheStructures {
private:
    std::list<std::pair<int, int>> itemList;
    std::unordered_map<int, std::list<std::pair<int, int>>::iterator> cacheMap;

public:
    MRUCache(int cap) : CacheStructures(cap) {}

    void put(int key, int value) {
        auto it = cacheMap.find(key);
        if (it != cacheMap.end()) {
            itemList.splice(itemList.begin(), itemList, it->second);
            it->second->second = value;
            return;
        }
        if (itemList.size() >= static_cast<size_t>(capacity)) {
            // Evict from front (MRU item) instead of back (LRU item)
            int mruKey = itemList.front().first;
            itemList.pop_front();
            cacheMap.erase(mruKey);
        }
        itemList.emplace_front(key, value);
        cacheMap[key] = itemList.begin();
    }
};