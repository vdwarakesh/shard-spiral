# Dense Matrix is a special type of Matrix where nearly all cells contain active values, explicitly allocating storage for every M x N cell contiguously.
class DenseMatrix(Matrix):
    def __init__(self, data_2d):
        rows = len(data_2d)
        cols = len(data_2d[0]) if rows > 0 else 0
        super().__init__(rows, cols)
        # Copy full 2D grid data explicitly
        for r in range(rows):
            for c in range(cols):
                self.grid[r][c] = data_2d[r][c]