# Heap is a special type of Tree-based structure that satisfies the Heap Property: every parent node is ordered by priority relative to its children, placing the global extreme (min or max) element right at the root.
class Heap(Tree):
    def __init__(self):
        super().__init__()

    def peek(self):
        # Return the highest-priority element stationed at the root
        return self.root.data if self.root else None