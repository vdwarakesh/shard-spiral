import java.util.LinkedList;

// HashTable is a special type of HashBasedStructures that combines a bucket array with collision resolution (separate chaining using linked lists).
public class HashTable extends HashBasedStructures {
    protected static class Entry {
        Object key;
        Object value;
        Entry(Object key, Object value) {
            this.key = key;
            this.value = value;
        }
    }

    // Array of LinkedLists to handle hash collisions in each bucket.
    // Note: Java arrays can hold data structures like LinkedList<Entry> as elements.
    protected LinkedList<Entry>[] buckets;

    @SuppressWarnings("unchecked")
    public HashTable(int numBuckets) {
        super(numBuckets);
        this.buckets = new LinkedList[numBuckets];
        for (int i = 0; i < numBuckets; i++) {
            this.buckets[i] = new LinkedList<>();
        }
    }
}