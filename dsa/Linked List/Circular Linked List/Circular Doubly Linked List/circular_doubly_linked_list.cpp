// CircularDoublyLinkedList is a special type of CircularLinkedList that connects tail->next to head and head->prev to tail for continuous bidirectional looping.
class CircularDoublyLinkedList : public CircularLinkedList {
public:
    CircularDoublyLinkedList() : CircularLinkedList() {}

    void insert(int data) {
        Node* newNode = new Node(data);
        if (head == nullptr) {
            head = tail = newNode;
            newNode->next = newNode;
            newNode->prev = newNode;
        } else {
            newNode->prev = tail;
            newNode->next = head;
            tail->next = newNode;
            head->prev = newNode;
            tail = newNode;
        }
        size++;
    }
};