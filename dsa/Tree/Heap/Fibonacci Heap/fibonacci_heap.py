# Fibonacci Heap is a special type of Heap that uses a circular doubly linked list of heap-ordered trees and lazy consolidation for O(1) amortized insert, merge, and decrease-key.
class FibonacciNode(TreeNode):
    def __init__(self, key):
        super().__init__(key)
        self.degree = 0
        self.marked = False   # Tracks whether this node has lost a child (for cascading cuts)
        self.parent = None
        self.child = None
        self.left = self      # Circular doubly linked list pointers
        self.right = self


class FibonacciHeap(Heap):
    def __init__(self):
        super().__init__()
        self.min_node = None  # Direct pointer to the minimum root for O(1) peek
        self.total_nodes = 0