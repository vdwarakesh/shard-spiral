// LiChaoTree is a special type of SegmentTree that stores linear functions (y = mx + b) to dynamically answer convex-hull maximum/minimum queries at any x in O(log X) time.
public class LiChaoTree extends SegmentTree {
    public static class Line {
        public long m; // Slope
        public long b; // Intercept

        public Line(long m, long b) {
            this.m = m;
            this.b = b;
        }

        public long eval(long x) {
            return m * x + b;
        }
    }

    // Array of Line objects storing the winning line at each interval's midpoint
    protected Line[] lineTree;

    public LiChaoTree(int domainSize) {
        super(new int[0]);
        this.n = domainSize;
        this.lineTree = new Line[4 * domainSize];
    }
}