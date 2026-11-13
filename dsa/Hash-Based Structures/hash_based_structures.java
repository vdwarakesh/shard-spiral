// Base class for Hash-Based Structures, which map data directly to bucket indices using a mathematical hash function for O(1) average-case access.
public class HashBasedStructures {
    protected int numBuckets;

    public HashBasedStructures(int numBuckets) {
        this.numBuckets = numBuckets;
    }

    protected int hash(Object key) {
        // Convert key's hash code into a non-negative array bucket index
        return Math.abs(key.hashCode()) % this.numBuckets;
    }
}