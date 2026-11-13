// CircularDoublyLinkedList is a special type of CircularLinkedList with two-way pointers where tail.next points to head and head.prev points to tail.
public class CircularDoublyLinkedList extends CircularLinkedList {
    public CircularDoublyLinkedList() {
        super();
    }

    public void insert(int data) {
        Node newNode = new Node(data);
        if (this.head == null) {
            this.head = this.tail = newNode;
            newNode.next = newNode;
            newNode.prev = newNode;
        } else {
            // Wire both forward and backward wrap-around links
            newNode.prev = this.tail;
            newNode.next = this.head;
            this.tail.next = newNode;
            this.head.prev = newNode;
            this.tail = newNode;
        }
        this.size++;
    }
}