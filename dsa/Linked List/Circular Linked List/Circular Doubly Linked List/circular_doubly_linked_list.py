# Circular Doubly Linked List is a special type of Circular Linked List where every node has both 'next' and 'prev' pointers, and both ends wrap around
# (tail.next == head and head.prev == tail).
class CircularDoublyLinkedList(CircularLinkedList):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        new_node = DoublyNode(data)
        if self.head is None:
            self.head = self.tail = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            new_node.prev = self.tail
            new_node.next = self.head
            self.tail.next = new_node
            self.head.prev = new_node
            self.tail = new_node
        self.size += 1