# include <vector> include <unordered_map> include <utility>

// Base class representing a Graph network structure containing vertices and edges.
class Graph {
public:
    struct Edge {
        int targetVertex;
        int weight;
        Edge(int t, int w) : targetVertex(t), weight(w) {}
    };

protected:
    // Adjacency list: vertex -> list of outgoing Edges.
    // Can also be represented using a 2D matrix (vector<vector<int>>) for Adjacency Matrix.
    std::unordered_map<int, std::vector<Edge>> adjList;
    bool directed;

public:
    Graph(bool isDirected = false) : directed(isDirected) {}
    virtual ~Graph() = default;

    void addEdge(int u, int v, int weight = 1) {
        adjList[u].emplace_back(v, weight);
        if (!directed) {
            adjList[v].emplace_back(u, weight);
        }
    }
};