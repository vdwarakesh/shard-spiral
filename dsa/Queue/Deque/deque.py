# Deque (Double-Ended Queue) is a special type of Queue that allows elements to be inserted and removed from both the front and the back in O(1) time.
class Deque(Queue):
    def __init__(self):
        super().__init__()

    def push_front(self, item):
        # Insert item at the front end of the deque
        self._items.appendleft(item)

    def push_back(self, item):
        # Insert item at the rear end of the deque
        self._items.append(item)

    def pop_front(self):
        # Remove item from the front end
        return self._items.popleft()

    def pop_back(self):
        # Remove item from the rear end
        return self._items.pop()