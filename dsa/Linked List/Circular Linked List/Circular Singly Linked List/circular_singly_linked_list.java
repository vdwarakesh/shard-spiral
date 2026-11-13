// CircularSinglyLinkedList is a special type of CircularLinkedList with one-way forward links where the tail node's 'next' pointer wraps around to the head.
public class CircularSinglyLinkedList extends CircularLinkedList {
    public CircularSinglyLinkedList() {
        super();
    }

    public void insert(int data) {
        Node newNode = new Node(data);
        if (this.head == null) {
            this.head = this.tail = newNode;
            newNode.next = this.head; // Points to itself
        } else {
            this.tail.next = newNode;
            this.tail = newNode;
            this.tail.next = this.head; // Close the forward ring
        }
        this.size++;
    }
}