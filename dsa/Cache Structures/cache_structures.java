// Base class for Cache Structures combining O(1) hash maps with eviction policies.
public class CacheStructures {
    protected int capacity;

    public CacheStructures(int capacity) {
        this.capacity = capacity;
    }
}