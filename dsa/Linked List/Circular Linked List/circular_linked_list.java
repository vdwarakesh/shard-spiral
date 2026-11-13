// CircularLinkedList is a special type of LinkedList where the last node links back to the first node instead of null, forming a continuous loop.
public class CircularLinkedList extends LinkedList {
    public CircularLinkedList() {
        super();
    }

    public boolean isCircular() {
        // In any non-empty circular list, tail.next points back to head
        return this.tail != null && this.tail.next == this.head;
    }
}