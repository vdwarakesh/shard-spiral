// Base class representing a First-In, First-Out (FIFO) Queue data structure.
// New elements enter at the rear and exit from the front in arrival order.
public class Queue {
    // Homogeneous storage array (can also be replaced with Object[] or a LinkedList)
    protected int[] data;
    protected int front;
    protected int rear;
    protected int size;
    protected int capacity;

    public Queue(int capacity) {
        this.capacity = capacity;
        this.data = new int[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }

    public void enqueue(int value) {
        this.data[++this.rear] = value;
        this.size++;
    }

    public int dequeue() {
        this.size--;
        return this.data[this.front++];
    }

    public boolean isEmpty() {
        return this.size == 0;
    }
}