// SinglyLinkedList is a special type of LinkedList where each node links strictly forward to the next node, ending at nullptr.
class SinglyLinkedList : public LinkedList {
public:
    SinglyLinkedList() : LinkedList() {}

    void insertFront(int data) {
        // Allocate a new node and point it to the old head
        Node* newNode = new Node(data);
        newNode->next = head;
        head = newNode;
        if (tail == nullptr) {
            tail = newNode;
        }
        size++;
    }

    void insertBack(int data) {
        // Link a new node at the end of the chain
        Node* newNode = new Node(data);
        if (tail == nullptr) {
            head = tail = newNode;
        } else {
            tail->next = newNode;
            tail = newNode;
        }
        size++;
    }
};