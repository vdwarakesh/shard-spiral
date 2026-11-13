# Static Array is a special type of Array whose capacity is fixed upon creation.
# Since Python lists are dynamic by default, we wrap a fixed-size list inside a class to enforce the static capacity constraint.
class StaticArray:
    def __init__(self, capacity):
        # Fixed capacity that cannot grow or shrink
        self.capacity = capacity
        # Pre-allocate contiguous slots initialized to None
        self.data = [None] * capacity

    def set(self, index, value):
        # Update element at a valid index within the fixed bounds
        if 0 <= index < self.capacity:
            self.data[index] = value
        else:
            raise IndexError("Index out of bounds for Static Array")

    def get(self, index):
        # Retrieve element in O(1) constant time by index
        if 0 <= index < self.capacity:
            return self.data[index]
        raise IndexError("Index out of bounds for Static Array")