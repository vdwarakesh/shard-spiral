# include <unordered_map>

// EulerTourTree is a special type of dynamic Tree that stores the Euler tour sequence inside a balanced BST so every subtree corresponds to a contiguous tour segment.
class EulerTourTree : public Tree {
public:
    struct TourNode : public TreeNode {
        TourNode* left = nullptr;
        TourNode* right = nullptr;
        TourNode* parent = nullptr;
        int subtreeSize = 1;

        TourNode(int vertexId) : TreeNode(vertexId) {}
    };

protected:
    std::unordered_map<int, TourNode*> firstVisit;
    std::unordered_map<int, TourNode*> lastVisit;

public:
    EulerTourTree() : Tree() {}
};