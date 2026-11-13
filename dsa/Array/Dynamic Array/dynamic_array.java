// DynamicArray is a special type of Array that automatically grows when full.
// Inherits from the base Array class.
// (In standard Java, java.util.ArrayList<E> provides a generic Dynamic Array).
public class DynamicArray extends Array {
    private int size;      // Number of elements currently stored
    private int capacity;  // Total allocated slots in the underlying array

    public DynamicArray(int initialCapacity) {
        this.capacity = initialCapacity;
        this.size = 0;
        // Homogeneous array of ints (can also be Object[] or any other data structure)
        this.data = new int[initialCapacity];
    }

    public void append(int value) {
        // Double the capacity when the underlying static array fills up
        if (this.size == this.capacity) {
            resize(this.capacity * 2);
        }
        this.data[this.size++] = value;
    }

    private void resize(int newCapacity) {
        // Create a new larger array and copy all elements from the old array
        int[] newData = new int[newCapacity];
        for (int i = 0; i < this.size; i++) {
            newData[i] = this.data[i];
        }
        this.data = newData;
        this.capacity = newCapacity;
    }
}