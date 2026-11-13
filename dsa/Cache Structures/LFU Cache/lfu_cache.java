import java.util.HashMap;
import java.util.LinkedHashSet;

// LFUCache is a special type of CacheStructures that evicts items with the lowest access frequency count first.
public class LFUCache extends CacheStructures {
    protected int minFreq;
    protected HashMap<Integer, Integer> vals;
    protected HashMap<Integer, Integer> counts;
    protected HashMap<Integer, LinkedHashSet<Integer>> lists;

    public LFUCache(int capacity) {
        super(capacity);
        this.minFreq = 0;
        this.vals = new HashMap<>();
        this.counts = new HashMap<>();
        this.lists = new HashMap<>();
        this.lists.put(1, new LinkedHashSet<>());
    }
}