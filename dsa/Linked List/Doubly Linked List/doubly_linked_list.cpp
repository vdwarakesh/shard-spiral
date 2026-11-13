// DoublyLinkedList is a special type of LinkedList where every node holds both
// 'next' and 'prev' pointers for bidirectional movement.
class DoublyLinkedList : public LinkedList {
public:
    DoublyLinkedList() : LinkedList() {}

    void insertBack(int data) {
        Node* newNode = new Node(data);
        if (tail == nullptr) {
            head = tail = newNode;
        } else {
            newNode->prev = tail;
            tail->next = newNode;
            tail = newNode;
        }
        size++;
    }

    void removeNode(Node* node) {
        // Bypass and delete the given node in O(1) time
        if (node->prev != nullptr) node->prev->next = node->next;
        else head = node->next;

        if (node->next != nullptr) node->next->prev = node->prev;
        else tail = node->prev;

        delete node;
        size--;
    }
};