// Base class representing a Linked List data structure.
// Consists of dynamically allocated Nodes connected via pointers.
class LinkedList {
protected:
    struct Node {
        int data;    // Payload value (can be templated for any data structure)
        Node* next;  // Pointer to the next node in the sequence
        Node* prev;  // Pointer to the previous node (used by doubly linked subclasses)

        Node(int val) : data(val), next(nullptr), prev(nullptr) {}
    };

    Node* head; // Entry pointer to the first node
    Node* tail; // Pointer to the last node
    int size;

public:
    LinkedList() : head(nullptr), tail(nullptr), size(0) {}
    virtual ~LinkedList() = default;
};