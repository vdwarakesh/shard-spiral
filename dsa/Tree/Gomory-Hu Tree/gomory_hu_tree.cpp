# include <vector>

// GomoryHuTree is a special type of weighted Tree where the minimum edge weight on the path between any u and v equals the exact Min-Cut / Max-Flow between u and v.
class GomoryHuTree : public Tree {
protected:
    int numVertices;
    std::vector<int> parent;        // Tree parent of vertex i
    std::vector<int> edgeCutWeight; // Min-cut weight on the edge (i, parent[i])

public:
    GomoryHuTree(int v)
        : Tree(), numVertices(v), parent(v, 0), edgeCutWeight(v, 0) {}
};