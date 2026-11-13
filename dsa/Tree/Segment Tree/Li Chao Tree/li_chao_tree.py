# Li Chao Tree is a special type of Segment Tree that stores linear functions (y = m*x + b) in each node to find the minimum or maximum y-value at any x-coordinate in O(log X) time.
class Line:
    def __init__(self, m=0, b=float('inf')):
        self.m = m  # Slope
        self.b = b  # Y-intercept

    def eval(self, x):
        return self.m * x + self.b


class LiChaoTree(SegmentTree):
    def __init__(self, x_min, x_max):
        super().__init__([])
        self.x_min = x_min
        self.x_max = x_max
        # Each segment tree node stores the dominant Line at that interval's midpoint
        self.lines = [Line() for _ in range(4 * (x_max - x_min + 1))]