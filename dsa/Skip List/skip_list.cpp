# include <vector> include <cstdlib> include <climits>

// SkipList is a probabilistic structure stacking sorted linked-list express lanes for O(log n) performance.
class SkipList {
public:
    struct SkipNode {
        int val;
        std::vector<SkipNode*> forward;
        SkipNode(int v, int level) : val(v), forward(level + 1, nullptr) {}
    };

private:
    int maxLevel;
    int level;
    SkipNode* head;

public:
    SkipList(int maxLvl = 16) : maxLevel(maxLvl), level(0), head(new SkipNode(INT_MIN, maxLvl)) {}
};