# Max-Heap is a special type of Binary Heap where every parent node is greater than or equal to its children, keeping the maximum element at the root (index 0).
class MaxHeap(BinaryHeap):
    def __init__(self):
        super().__init__()

    def insert(self, val):
        # Add to bottom leaf and bubble up while larger than parent
        self.heap.append(val)
        i = len(self.heap) - 1
        while i > 0 and self.heap[i] > self.heap[self.parent(i)]:
            p = self.parent(i)
            self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
            i = p

    def get_max(self):
        return self.heap[0] if self.heap else None