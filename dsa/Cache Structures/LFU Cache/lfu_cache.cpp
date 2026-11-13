# include <unordered_map> include <list>

// LFUCache is a special type of CacheStructures tracking access frequencies to evict the least frequently requested items.
class LFUCache : public CacheStructures {
private:
    int minFreq;
    std::unordered_map<int, int> keyToVal;
    std::unordered_map<int, int> keyToFreq;
    std::unordered_map<int, std::list<int>> freqToList;
    std::unordered_map<int, std::list<int>::iterator> keyToIter;

public:
    LFUCache(int cap) : CacheStructures(cap), minFreq(0) {}
};