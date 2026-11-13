# Circular Queue is a special type of Queue that connects the end of a fixed-size array back to its beginning using modulo arithmetic to reuse empty front slots.
class CircularQueue(Queue):
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = [None] * capacity
        self.front = 0
        self.rear = -1
        self.size = 0

    def enqueue(self, item):
        if self.size == self.capacity:
            raise OverflowError("Circular Queue is full")
        # Wrap rear pointer around to index 0 using modulo arithmetic
        self.rear = (self.rear + 1) % self.capacity
        self.data[self.rear] = item
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            raise IndexError("Circular Queue is empty")
        item = self.data[self.front]
        # Advance front pointer around the ring
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item