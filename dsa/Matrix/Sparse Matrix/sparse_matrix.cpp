# include <map> include <utility>

// SparseMatrix is a special type of Matrix that stores only non-zero entries to save memory on largely empty 2D grids.
class SparseMatrix : public Matrix {
private:
    std::map<std::pair<int, int>, int> nzMap; // (row, col) -> non-zero value

public:
    SparseMatrix(int r, int c) : Matrix(r, c) {}

    void set(int r, int c, int val) {
        if (val != 0) nzMap[{r, c}] = val;
        else nzMap.erase({r, c});
    }

    int get(int r, int c) const {
        auto it = nzMap.find({r, c});
        return (it != nzMap.end()) ? it->second : 0;
    }
};