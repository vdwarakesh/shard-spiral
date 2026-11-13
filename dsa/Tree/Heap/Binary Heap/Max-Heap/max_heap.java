// MaxHeap is a special type of BinaryHeap where parent >= children, guaranteeing that the largest element in the collection is always at index 0 (the root).
public class MaxHeap extends BinaryHeap {
    public MaxHeap(int capacity) {
        super(capacity);
    }

    public void insert(int val) {
        int i = this.size++;
        this.heapArray[i] = val;
        // Sift up while current node is greater than its parent
        while (i > 0 && this.heapArray[i] > this.heapArray[parent(i)]) {
            int temp = this.heapArray[i];
            this.heapArray[i] = this.heapArray[parent(i)];
            this.heapArray[parent(i)] = temp;
            i = parent(i);
        }
    }

    public int getMax() {
        return this.heapArray[0];
    }
}