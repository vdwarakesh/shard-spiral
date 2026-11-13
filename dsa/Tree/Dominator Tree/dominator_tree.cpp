# include <vector>

// DominatorTree is a special type of Tree in which the parent of every node v is its
// Immediate Dominator (idom[v]), capturing mandatory control-flow/network bottlenecks.
class DominatorTree : public Tree {
protected:
    int entryRoot;
    std::vector<int> idom;                      // Immediate dominator (parent) of each node
    std::vector<std::vector<int>> domChildren;  // Children in the Dominator Tree

public:
    DominatorTree(int numVertices, int root = 0)
        : Tree(), entryRoot(root), idom(numVertices, -1), domChildren(numVertices) {
        idom[entryRoot] = entryRoot;
    }
};