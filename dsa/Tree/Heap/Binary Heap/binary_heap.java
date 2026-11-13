// BinaryHeap is a special type of Heap shaped as a Complete Binary Tree and stored compactly inside a flat array using index math (left = 2i + 1, right = 2i + 2).
public class BinaryHeap extends Heap {
    // Homogeneous integer array (can also hold any Comparable Object type)
    protected int[] heapArray;
    protected int size;
    protected int capacity;

    public BinaryHeap(int capacity) {
        super();
        this.capacity = capacity;
        this.size = 0;
        this.heapArray = new int[capacity];
    }

    protected int parent(int i) { return (i - 1) / 2; }
    protected int leftChild(int i) { return 2 * i + 1; }
    protected int rightChild(int i) { return 2 * i + 2; }
}