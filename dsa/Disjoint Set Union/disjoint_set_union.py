# Disjoint Set Union (DSU / Union-Find) keeps track of partitioned disjoint sets, supporting near-constant time group merging (union) and set representation checks (find).
class DisjointSetUnion:
    def __init__(self, n):
        # parent[i] points to the group representative leader; initially every element is its own boss
        self.parent = list(range(n))
        # rank tree heights used to keep union trees flat
        self.rank = [0] * n

    def find(self, i):
        # Path compression: flatten tree structure during find so future lookups are O(1)
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            # Union by rank: attach smaller rank tree under root of higher rank tree
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1