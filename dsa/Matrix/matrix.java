// Base class representing a 2D Matrix grid of rows and columns.
public class Matrix {
    // 2D homogeneous array (can also be double[][], char[][], or Object[][])
    protected int[][] grid;
    protected int rows;
    protected int cols;

    public Matrix(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.grid = new int[rows][cols];
    }

    public int get(int r, int c) {
        return this.grid[r][c];
    }

    public void set(int r, int c, int val) {
        this.grid[r][c] = val;
    }
}