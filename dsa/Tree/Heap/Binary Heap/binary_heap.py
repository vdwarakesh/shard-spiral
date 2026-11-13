# Binary Heap is a special type of Heap structured as a Complete Binary Tree, allowing it to be stored flat inside an array without explicit node pointers.
class BinaryHeap(Heap):
    def __init__(self):
        super().__init__()
        # Implicit complete binary tree stored in a contiguous list
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2