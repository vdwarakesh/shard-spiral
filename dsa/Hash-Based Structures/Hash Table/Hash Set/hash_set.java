// HashSet is a special type of HashTable that stores a collection of unique keys with no duplicate entries and no extra values.
public class HashSet extends HashTable {
    // Dummy placeholder value used so HashSet can reuse HashTable's Entry buckets
    private static final Object PRESENT = new Object();

    public HashSet(int numBuckets) {
        super(numBuckets);
    }

    public void add(Object key) {
        int idx = hash(key);
        for (Entry entry : this.buckets[idx]) {
            if (entry.key.equals(key)) return; // Ignore duplicates
        }
        this.buckets[idx].add(new Entry(key, PRESENT));
    }

    public boolean contains(Object key) {
        int idx = hash(key);
        for (Entry entry : this.buckets[idx]) {
            if (entry.key.equals(key)) return true;
        }
        return false;
    }
}