# A Graph is a non-linear network structure consisting of vertices (nodes) connected by edges. Unlike trees, graphs allow arbitrary many-to-many connections and cycles.
class Graph:
    def __init__(self, directed=False):
        # Adjacency list representation mapping vertex -> list of neighbor vertices
        self.adj_list = {}
        self.directed = directed  # False = undirected graph, True = directed graph (digraph)

    def add_vertex(self, v):
        if v not in self.adj_list:
            self.adj_list[v] = []

    def add_edge(self, u, v, weight=1):
        # Ensure both vertices exist
        self.add_vertex(u)
        self.add_vertex(v)
        # Store edge as neighbor or (neighbor, weight) tuple
        self.adj_list[u].append((v, weight))
        if not self.directed:
            self.adj_list[v].append((u, weight))