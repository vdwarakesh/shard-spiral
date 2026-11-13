import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Base class representing a Graph network structure composed of vertices and edges.
public class Graph {
    public static class Edge {
        public int targetVertex;
        public int weight;

        public Edge(int target, int weight) {
            this.targetVertex = target;
            this.weight = weight;
        }
    }

    // Adjacency list: maps vertex ID to a list of connected Edges.
    // Note: Can also use int[][] for an Adjacency Matrix representation.
    protected Map<Integer, List<Edge>> adjacencyList;
    protected boolean isDirected;

    public Graph(boolean isDirected) {
        this.adjacencyList = new HashMap<>();
        this.isDirected = isDirected;
    }

    public void addVertex(int v) {
        this.adjacencyList.putIfAbsent(v, new ArrayList<>());
    }

    public void addEdge(int u, int v, int weight) {
        addVertex(u);
        addVertex(v);
        this.adjacencyList.get(u).add(new Edge(v, weight));
        if (!isDirected) {
            this.adjacencyList.get(v).add(new Edge(u, weight));
        }
    }
}