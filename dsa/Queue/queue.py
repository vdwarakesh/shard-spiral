from collections import deque

# A Queue is a linear data structure following First-In, First-Out (FIFO) order.
# Elements enter at the rear (enqueue) and leave from the front (dequeue).
class Queue:
    def __init__(self):
        # collections.deque provides O(1) appends and pops from both ends
        self._items = deque()

    def enqueue(self, item):
        # Add an element to the back of the waiting line
        self._items.append(item)

    def dequeue(self):
        # Remove and return the oldest element from the front of the line
        if not self.is_empty():
            return self._items.popleft()
        raise IndexError("Dequeue from an empty Queue")

    def peek(self):
        return self._items[0] if not self.is_empty() else None

    def is_empty(self):
        return len(self._items) == 0