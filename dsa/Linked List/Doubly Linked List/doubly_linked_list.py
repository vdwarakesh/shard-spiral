# Doubly Linked List is a special type of Linked List where each node maintains two pointers: 'next' (forward) and 'prev' (backward) for two-way navigation.
class DoublyNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.prev = None  # Backward link to the preceding node


class DoublyLinkedList(LinkedList):
    def __init__(self):
        super().__init__()

    def insert_back(self, data):
        # Link the new node both forward from the old tail and backward to the old tail
        new_node = DoublyNode(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_node(self, node):
        # O(1) node removal made possible by having direct access to 'prev' and 'next'
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1