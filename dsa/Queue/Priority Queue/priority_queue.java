// PriorityQueue is a special type of Queue where elements are dequeued according to their priority score rather than First-In, First-Out arrival time.
public class PriorityQueue extends Queue {
    public PriorityQueue(int capacity) {
        super(capacity);
    }

    @Override
    public void enqueue(int value) {
        // Insert element and sift it up to maintain min-heap priority order
        int i = this.size++;
        this.data[i] = value;
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (this.data[parent] <= this.data[i]) break;
            int temp = this.data[parent];
            this.data[parent] = this.data[i];
            this.data[i] = temp;
            i = parent;
        }
    }

    @Override
    public int dequeue() {
        // Extract the highest-priority (minimum) element at index 0
        int min = this.data[0];
        this.data[0] = this.data[--this.size];
        int i = 0;
        while (true) {
            int left = 2 * i + 1, right = 2 * i + 2, smallest = i;
            if (left < this.size && this.data[left] < this.data[smallest]) smallest = left;
            if (right < this.size && this.data[right] < this.data[smallest]) smallest = right;
            if (smallest == i) break;
            int temp = this.data[i];
            this.data[i] = this.data[smallest];
            this.data[smallest] = temp;
            i = smallest;
        }
        return min;
    }
}