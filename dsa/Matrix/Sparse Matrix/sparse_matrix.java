import java.util.HashMap;
import java.util.Map;

// SparseMatrix is a special type of Matrix that compresses mostly-zero grids by recording only non-zero entries via coordinate maps or Compressed Sparse Row (CSR).
public class SparseMatrix extends Matrix {
    public static class Coordinate {
        public int row, col;
        public Coordinate(int r, int c) { this.row = r; this.col = c; }
        @Override
        public boolean equals(Object o) {
            Coordinate c = (Coordinate) o;
            return this.row == c.row && this.col == c.col;
        }
        @Override public int hashCode() { return Objects.hash(row, col); }
    }

    protected Map<String, Integer> nzMap; // "row,col" -> value

    public SparseMatrix(int rows, int cols) {
        super(rows, cols);
        this.nzMap = new HashMap<>();
    }

    @Override
    public void set(int r, int c, int val) {
        String key = r + "," + c;
        if (val != 0) nzMap.put(key, val);
        else nzMap.remove(key);
    }

    @Override
    public int get(int r, int c) {
        return nzMap.getOrDefault(r + "," + c, 0);
    }
}