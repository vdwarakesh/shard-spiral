// CircularSinglyLinkedList is a special type of CircularLinkedList where nodes have a single forward 'next' pointer that loops from tail back to head.
class CircularSinglyLinkedList : public CircularLinkedList {
public:
    CircularSinglyLinkedList() : CircularLinkedList() {}

    void insert(int data) {
        Node* newNode = new Node(data);
        if (head == nullptr) {
            head = tail = newNode;
            newNode->next = head;
        } else {
            tail->next = newNode;
            tail = newNode;
            tail->next = head; // Complete the one-way circular loop
        }
        size++;
    }
};