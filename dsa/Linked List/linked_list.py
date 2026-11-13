# A Linked List is a linear data structure where elements (Nodes) are stored in scattered memory locations and connected together via pointers.
class Node:
    def __init__(self, data):
        self.data = data  # The value stored in the node
        self.next = None  # Pointer to the next node in the chain


class LinkedList:
    def __init__(self):
        # Head points to the very first node in the linked list
        self.head = None
        # Tail points to the last node for fast O(1) appends
        self.tail = None
        self.size = 0