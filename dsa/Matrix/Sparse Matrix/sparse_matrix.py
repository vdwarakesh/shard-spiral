# Sparse Matrix is a special type of Matrix where most cells are zero, compressing memory by storing only non-zero values along with their (row, col) coordinates.
class SparseMatrix(Matrix):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        # Dictionary mapping (row, col) -> non-zero value
        self.non_zero_dict = {}

    def set(self, r, c, val):
        if val != 0:
            self.non_zero_dict[(r, c)] = val
        elif (r, c) in self.non_zero_dict:
            del self.non_zero_dict[(r, c)]

    def get(self, r, c):
        return self.non_zero_dict.get((r, c), 0)