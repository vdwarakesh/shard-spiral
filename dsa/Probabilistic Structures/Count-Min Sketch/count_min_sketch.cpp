# include <vector> include <string> include <algorithm>

// CountMinSketch is a special type of ProbabilisticStructures that estimates stream item frequencies using d rows and w columns of hashed counters.
class CountMinSketch : public ProbabilisticStructures {
private:
    std::vector<std::vector<int>> table;
    int w, d;

public:
    CountMinSketch(int width, int depth) : ProbabilisticStructures(0.01), w(width), d(depth), table(depth, std::vector<int>(width, 0)) {}
};