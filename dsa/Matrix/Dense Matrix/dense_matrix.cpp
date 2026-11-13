# include <vector>

// DenseMatrix is a special type of Matrix storing every cell in a dense 2D grid.
class DenseMatrix : public Matrix {
public:
    DenseMatrix(const std::vector<std::vector<int>>& data2D)
        : Matrix(data2D.size(), data2D.empty() ? 0 : data2D[0].size()) {
        grid = data2D;
    }
};