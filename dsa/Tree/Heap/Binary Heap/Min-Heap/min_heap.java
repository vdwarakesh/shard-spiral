// MinHeap is a special type of BinaryHeap where parent <= children, guaranteeing that the smallest element in the collection is always at index 0 (the root).
public class MinHeap extends BinaryHeap {
    public MinHeap(int capacity) {
        super(capacity);
    }

    public void insert(int val) {
        int i = this.size++;
        this.heapArray[i] = val;
        // Sift up until parent is smaller than or equal to current node
        while (i > 0 && this.heapArray[i] < this.heapArray[parent(i)]) {
            int temp = this.heapArray[i];
            this.heapArray[i] = this.heapArray[parent(i)];
            this.heapArray[parent(i)] = temp;
            i = parent(i);
        }
    }

    public int getMin() {
        return this.heapArray[0];
    }
}