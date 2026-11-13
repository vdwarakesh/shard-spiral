// Base class for Probabilistic Structures providing approximate stream analytics within tunable error bounds.
class ProbabilisticStructures {
protected:
    double errorRate;

public:
    ProbabilisticStructures(double err = 0.01) : errorRate(err) {}
    virtual ~ProbabilisticStructures() = default;
};