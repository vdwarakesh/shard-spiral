# Singly Linked List is a special type of Linked List where each node has only one pointer ('next') pointing strictly forward to the succeeding node.
class SinglyLinkedList(LinkedList):
    def __init__(self):
        super().__init__()

    def insert_front(self, data):
        # Create a new node and wire its next pointer to the current head
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        self.size += 1

    def insert_back(self, data):
        # Attach a new node at the end of the one-way chain
        new_node = Node(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1