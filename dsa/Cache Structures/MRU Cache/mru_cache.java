// MRUCache is a special type of CacheStructures that evicts the most recently used item first, ideal for sequential cyclic scans over large datasets.
public class MRUCache extends CacheStructures {
    protected LinkedHashMap<Integer, Integer> map;

    public MRUCache(int capacity) {
        super(capacity);
        this.map = new LinkedHashMap<>(capacity, 0.75f, true);
    }

    public void put(int key, int value) {
        if (map.size() >= capacity && !map.containsKey(key)) {
            // Remove the newest (most recently used) entry
            Integer newestKey = null;
            for (Integer k : map.keySet()) newestKey = k;
            if (newestKey != null) map.remove(newestKey);
        }
        map.put(key, value);
    }
}