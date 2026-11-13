// TopTree is a special type of dynamic Tree that contracts tree clusters with at most two boundary vertices using Compress and Rake operations.
class TopTree : public Tree {
public:
    enum ClusterType { BASE_EDGE, COMPRESS, RAKE };

    struct ClusterNode : public TreeNode {
        ClusterType type;
        int boundaryU;
        int boundaryV;
        ClusterNode* leftCluster = nullptr;
        ClusterNode* rightCluster = nullptr;

        ClusterNode(ClusterType t, int u, int v)
            : TreeNode(0), type(t), boundaryU(u), boundaryV(v) {}
    };

protected:
    ClusterNode* topRoot = nullptr;

public:
    TopTree() : Tree() {}
};