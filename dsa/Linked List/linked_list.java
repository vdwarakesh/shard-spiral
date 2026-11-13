// Base class representing a Linked List data structure.
// Elements are wrapped inside Nodes connected by references rather than contiguous memory.
public class LinkedList {
    // Node building block holding data and a reference to the next node
    protected static class Node {
        int data;   // Can hold any data type or object
        Node next;  // Reference to the following node
        Node prev;  // Optional backward reference used by doubly-linked subclasses

        Node(int data) {
            this.data = data;
            this.next = null;
            this.prev = null;
        }
    }

    protected Node head; // First node in the list
    protected Node tail; // Last node in the list
    protected int size;  // Total number of nodes

    public LinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }
}