# Min-Heap is a special type of Binary Heap where every parent node is less than or equal to its children, keeping the minimum element at the root (index 0).
class MinHeap(BinaryHeap):
    def __init__(self):
        super().__init__()

    def insert(self, val):
        # Add to bottom leaf and bubble up while smaller than parent
        self.heap.append(val)
        i = len(self.heap) - 1
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:
            p = self.parent(i)
            self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
            i = p

    def get_min(self):
        return self.heap[0] if self.heap else None