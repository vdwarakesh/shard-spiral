// DenseMatrix is a special type of Matrix where most cells are non-zero, allocating full M x N contiguous storage.
public class DenseMatrix extends Matrix {
    public DenseMatrix(int[][] data2D) {
        super(data2D.length, data2D.length > 0 ? data2D[0].length : 0);
        for (int r = 0; r < rows; r++) {
            System.arraycopy(data2D[r], 0, this.grid[r], 0, cols);
        }
    }
}