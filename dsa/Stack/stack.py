# A Stack is a linear data structure following Last-In, First-Out (LIFO) order.
# All insertions (push) and removals (pop) occur exclusively at the top end.
class Stack:
    def __init__(self):
        # Underlying dynamic list storing stack elements
        self._items = []

    def push(self, item):
        # Place a new item on top of the stack in O(1) amortized time
        self._items.append(item)

    def pop(self):
        # Remove and return the most recently added item from the top
        if not self.is_empty():
            return self._items.pop()
        raise IndexError("Pop from an empty Stack")

    def peek(self):
        # Inspect the top item without removing it
        if not self.is_empty():
            return self._items[-1]
        return None

    def is_empty(self):
        return len(self._items) == 0