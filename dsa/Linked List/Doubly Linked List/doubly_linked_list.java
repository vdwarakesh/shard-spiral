// DoublyLinkedList is a special type of LinkedList where every node links both forward ('next') and backward ('prev'), allowing bidirectional traversal and O(1) deletion.
public class DoublyLinkedList extends LinkedList {
    public DoublyLinkedList() {
        super();
    }

    public void insertBack(int data) {
        Node newNode = new Node(data);
        if (this.tail == null) {
            this.head = this.tail = newNode;
        } else {
            // Wire two-way links between the old tail and the new node
            newNode.prev = this.tail;
            this.tail.next = newNode;
            this.tail = newNode;
        }
        this.size++;
    }

    public void removeNode(Node node) {
        // Splice a node out of the list in O(1) time using its prev and next links
        if (node.prev != null) {
            node.prev.next = node.next;
        } else {
            this.head = node.next;
        }
        if (node.next != null) {
            node.next.prev = node.prev;
        } else {
            this.tail = node.prev;
        }
        this.size--;
    }
}