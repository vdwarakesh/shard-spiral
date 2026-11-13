// StaticArray is a special type of Array with a permanently fixed size.
// Inherits from the base Array class.
public class StaticArray extends Array {
    private final int capacity;

    public StaticArray(int capacity) {
        this.capacity = capacity;
        // Allocate a fixed-size homogeneous integer array.
        // Note: You can also use other data types or objects (e.g., String[], Object[])
        this.data = new int[capacity];
    }

    public void set(int index, int value) {
        // Assign value at index in O(1) time; size can never be expanded
        this.data[index] = value;
    }

    public int get(int index) {
        return this.data[index];
    }
}