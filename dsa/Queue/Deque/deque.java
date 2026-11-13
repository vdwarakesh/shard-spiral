// Deque (Double-Ended Queue) is a special type of Queue that supports inserting and removing elements from both the front and rear ends.
public class Deque extends Queue {
    public Deque(int capacity) {
        super(capacity);
    }

    public void pushFront(int value) {
        // Move front backward with circular wrap-around and insert element
        this.front = (this.front - 1 + this.capacity) % this.capacity;
        this.data[this.front] = value;
        this.size++;
    }

    public void pushBack(int value) {
        this.rear = (this.rear + 1) % this.capacity;
        this.data[this.rear] = value;
        this.size++;
    }

    public int popFront() {
        int val = this.data[this.front];
        this.front = (this.front + 1) % this.capacity;
        this.size--;
        return val;
    }

    public int popBack() {
        int val = this.data[this.rear];
        this.rear = (this.rear - 1 + this.capacity) % this.capacity;
        this.size--;
        return val;
    }
}