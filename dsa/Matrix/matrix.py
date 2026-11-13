# A Matrix is a 2D data structure organizing elements into rows and columns, accessible via (row, column) coordinate indexing.
class Matrix:
    def __init__(self, rows, cols, default_val=0):
        self.rows = rows
        self.cols = cols
        # 2D list (list of lists) representing the grid
        self.grid = [[default_val for _ in range(cols)] for _ in range(rows)]

    def get(self, r, c):
        return self.grid[r][c]

    def set(self, r, c, val):
        self.grid[r][c] = val