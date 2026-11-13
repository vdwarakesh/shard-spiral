# Dynamic Array is a special type of Array that automatically resizes itself when it runs out of capacity.
# Python's built-in list is implemented as a Dynamic Array under the hood in C.
dynamic_arr = [10, 20, 30]
dynamic_arr.append(40)  # Automatically expands capacity when full

# Explicit class implementation showing how Dynamic Array extends StaticArray:
class DynamicArray(StaticArray):
    def __init__(self, initial_capacity=4):
        super().__init__(initial_capacity)
        # Logical size tracks actual number of elements currently stored
        self.size = 0

    def append(self, value):
        # If logical size reaches physical capacity, double the underlying array size
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = value
        self.size += 1

    def _resize(self, new_capacity):
        # Allocate a larger contiguous block and copy existing elements over
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity