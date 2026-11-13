// CircularQueue is a special type of Queue that wraps around a fixed-size array using modulo arithmetic so vacated slots at the front are automatically reused.
public class CircularQueue extends Queue {
    public CircularQueue(int capacity) {
        super(capacity);
    }

    @Override
    public void enqueue(int value) {
        if (this.size == this.capacity) {
            throw new IllegalStateException("CircularQueue is full");
        }
        // Wrap around to index 0 when reaching the end of the array
        this.rear = (this.rear + 1) % this.capacity;
        this.data[this.rear] = value;
        this.size++;
    }

    @Override
    public int dequeue() {
        if (this.size == 0) {
            throw new IllegalStateException("CircularQueue is empty");
        }
        int val = this.data[this.front];
        this.front = (this.front + 1) % this.capacity;
        this.size--;
        return val;
    }
}