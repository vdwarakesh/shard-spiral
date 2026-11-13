# include <vector> include <numeric>

// DisjointSetUnion (Union-Find) manages disjoint groups with path compression and union by rank.
class DisjointSetUnion {
protected:
    std::vector<int> parent;
    std::vector<int> rankTree;

public:
    DisjointSetUnion(int n) : parent(n), rankTree(n, 0) {
        std::iota(parent.begin(), parent.end(), 0); // parent[i] = i
    }

    int find(int i) {
        if (parent[i] != i) {
            parent[i] = find(parent[i]); // Path compression flattens the tree
        }
        return parent[i];
    }

    void unionSets(int i, int j) {
        int rootI = find(i);
        int rootJ = find(j);
        if (rootI != rootJ) {
            if (rankTree[rootI] < rankTree[rootJ]) {
                parent[rootI] = rootJ;
            } else if (rankTree[rootI] > rankTree[rootJ]) {
                parent[rootJ] = rootI;
            } else {
                parent[rootJ] = rootI;
                rankTree[rootI]++;
            }
        }
    }
};