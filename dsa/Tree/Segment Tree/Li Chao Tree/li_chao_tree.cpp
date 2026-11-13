# include <vector> include <limits>

// LiChaoTree is a special type of SegmentTree that maintains the dominant line segment
// (y = mx + b) at each interval's midpoint for O(log X) function extremum queries.
class LiChaoTree : public SegmentTree {
public:
    struct Line {
        long long m, b;
        Line(long long slope = 0, long long intercept = std::numeric_limits<long long>::max())
            : m(slope), b(intercept) {}

        long long eval(long long x) const { return m * x + b; }
    };

protected:
    std::vector<Line> lineTree;

public:
    LiChaoTree(int domainSize) : SegmentTree(), lineTree(4 * domainSize) {
        n = domainSize;
    }
};