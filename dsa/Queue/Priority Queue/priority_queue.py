import heapq

# Priority Queue is a special type of Queue where elements are served based on priority order rather than arrival order.
class PriorityQueue(Queue):
    def __init__(self):
        # Backed by a binary heap so the highest-priority (smallest key) item is always at index 0
        self._heap = []

    def enqueue(self, item, priority=0):
        # Push a (priority, item) tuple onto the heap in O(log n) time
        heapq.heappush(self._heap, (priority, item))

    def dequeue(self):
        # Pop and return the item with the highest priority (lowest priority number)
        if self._heap:
            return heapq.heappop(self._heap)[1]
        raise IndexError("Dequeue from an empty PriorityQueue")