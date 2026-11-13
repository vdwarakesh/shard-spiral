# Circular Singly Linked List is a special type of Circular Linked List where each node has only one forward pointer, and the tail's next pointer loops to head.
class CircularSinglyLinkedList(CircularLinkedList):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = self.tail = new_node
            # Single node loops back to itself
            new_node.next = self.head
        else:
            self.tail.next = new_node
            self.tail = new_node
            # Maintain the one-way ring by pointing the new tail back to head
            self.tail.next = self.head
        self.size += 1