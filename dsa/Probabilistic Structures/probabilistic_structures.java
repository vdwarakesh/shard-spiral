// Base class for Probabilistic Structures (Data Sketches) that trade a small mathematical error bound for sublinear memory usage.
public class ProbabilisticStructures {
    protected double targetErrorRate;

    public ProbabilisticStructures(double errorRate) {
        this.targetErrorRate = errorRate;
    }
}