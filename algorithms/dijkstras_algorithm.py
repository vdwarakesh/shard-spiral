import heapq

def dijkstras_algorithm(graph, start_node=None):
    if not graph:
        return {}
    if start_node is None:
        start_node = next(iter(graph))
    if start_node not in graph:
        return {}
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    pq = [(0, start_node)]
    visited = []
    while pq:
        curr_dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.append(node)
        for neighbor, weight in graph[node]:
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances