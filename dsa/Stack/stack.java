// A Stack is a Last-In, First-Out (LIFO) linear data structure where elements are pushed and popped strictly from the top.
public class Stack {
    // Homogeneous array storing stack elements (can also hold Objects or any data type)
    private int[] elements;
    private int top; // Index of the current top element

    public Stack(int capacity) {
        this.elements = new int[capacity];
        this.top = -1; // -1 indicates the stack is currently empty
    }

    public void push(int value) {
        // Increment top and place new element on the top of the stack
        this.elements[++this.top] = value;
    }

    public int pop() {
        // Return the top element and decrement top pointer
        return this.elements[this.top--];
    }

    public int peek() {
        return this.elements[this.top];
    }

    public boolean isEmpty() {
        return this.top == -1;
    }
}