# Circular Linked List is a special type of Linked List in which the tail node points directly back to the head node instead of None, forming an unbroken ring.
class CircularLinkedList(LinkedList):
    def __init__(self):
        super().__init__()

    def is_circular(self):
        # Verify the ring invariant: the tail's next pointer loops back to head
        return self.tail is not None and self.tail.next == self.head