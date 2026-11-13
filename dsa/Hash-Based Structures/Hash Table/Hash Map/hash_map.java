// HashMap is a special type of HashTable that stores unique Key-Value pairs.
// (In standard Java, java.util.HashMap<K, V> is the built-in implementation).
public class HashMap extends HashTable {
    public HashMap(int numBuckets) {
        super(numBuckets);
    }

    public void put(Object key, Object value) {
        int idx = hash(key);
        // Overwrite value if key already exists in the bucket chain
        for (Entry entry : this.buckets[idx]) {
            if (entry.key.equals(key)) {
                entry.value = value;
                return;
            }
        }
        this.buckets[idx].add(new Entry(key, value));
    }

    public Object get(Object key) {
        int idx = hash(key);
        for (Entry entry : this.buckets[idx]) {
            if (entry.key.equals(key)) {
                return entry.value;
            }
        }
        return null;
    }
}