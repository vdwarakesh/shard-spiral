import random

# Skip List is a probabilistic multi-layered data structure built from stacked sorted linked lists, achieving O(log n) search and update speeds without tree rotations.
class SkipListNode:
    def __init__(self, val, level):
        self.val = val
        # Homogeneous array of forward pointers for each express lane level
        self.forward = [None] * (level + 1)


class SkipList:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level
        self.p = p
        self.head = SkipListNode(-float('inf'), max_level)
        self.level = 0