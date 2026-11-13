import java.util.LinkedHashMap;
import java.util.Map;

// LRUCache is a special type of CacheStructures that evicts the least recently accessed item when full, using a Hash Map + Doubly Linked List hybrid.
public class LRUCache extends CacheStructures {
    protected LinkedHashMap<Integer, Integer> map;

    public LRUCache(int capacity) {
        super(capacity);
        // LinkedHashMap configured in access-order mode
        this.map = new LinkedHashMap<Integer, Integer>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
                return size() > capacity;
            }
        };
    }

    public int get(int key) {
        return map.getOrDefault(key, -1);
    }

    public void put(int key, int value) {
        map.put(key, value);
    }
}