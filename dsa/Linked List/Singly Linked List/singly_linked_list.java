// SinglyLinkedList is a special type of LinkedList where traversal is strictly one-way from head to tail using only the 'next' pointer.
public class SinglyLinkedList extends LinkedList {
    public SinglyLinkedList() {
        super();
    }

    public void insertFront(int data) {
        // Place a new node at the head of the list in O(1) time
        Node newNode = new Node(data);
        newNode.next = this.head;
        this.head = newNode;
        if (this.tail == null) {
            this.tail = newNode;
        }
        this.size++;
    }

    public void insertBack(int data) {
        // Append a new node after the current tail in O(1) time
        Node newNode = new Node(data);
        if (this.tail == null) {
            this.head = this.tail = newNode;
        } else {
            this.tail.next = newNode;
            this.tail = newNode;
        }
        this.size++;
    }
}