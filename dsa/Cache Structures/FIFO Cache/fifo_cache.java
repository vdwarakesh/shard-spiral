import java.util.LinkedHashMap;
import java.util.Map;

// FIFOCache is a special type of CacheStructures that evicts the oldest inserted item first in arrival order without updating timestamps on read hits.
public class FIFOCache extends CacheStructures {
    protected LinkedHashMap<Integer, Integer> map;

    public FIFOCache(int capacity) {
        super(capacity);
        // LinkedHashMap configured in insertion-order (false access-order)
        this.map = new LinkedHashMap<Integer, Integer>(capacity, 0.75f, false) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
                return size() > capacity;
            }
        };
    }

    public void put(int key, int value) {
        map.put(key, value);
    }
}