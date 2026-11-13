// CircularLinkedList is a special type of LinkedList in which the final node connects back to the first node to form a closed ring topology.
class CircularLinkedList : public LinkedList {
public:
    CircularLinkedList() : LinkedList() {}

    bool isCircular() const {
        return tail != nullptr && tail->next == head;
    }
};