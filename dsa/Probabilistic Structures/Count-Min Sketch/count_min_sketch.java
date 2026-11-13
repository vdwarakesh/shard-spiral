// CountMinSketch is a special type of ProbabilisticStructures estimating frequency counts in data streams using a 2D counter matrix.
public class CountMinSketch extends ProbabilisticStructures {
    protected int[][] table;
    protected int width;
    protected int depth;

    public CountMinSketch(int width, int depth) {
        super(0.01);
        this.width = width;
        this.depth = depth;
        this.table = new int[depth][width];
    }
}