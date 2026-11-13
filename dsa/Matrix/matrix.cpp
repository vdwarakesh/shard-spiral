# include <vector>

// Base class representing a 2D Matrix grid.
class Matrix {
protected:
    // 2D homogeneous vector representing grid cells (can be templated for any type)
    std::vector<std::vector<int>> grid;
    int rows;
    int cols;

public:
    Matrix(int r, int c, int defaultVal = 0)
        : rows(r), cols(c), grid(r, std::vector<int>(c, defaultVal)) {}

    virtual ~Matrix() = default;

    int get(int r, int c) const {
        return grid[r][c];
    }

    void set(int r, int c, int val) {
        grid[r][c] = val;
    }
};