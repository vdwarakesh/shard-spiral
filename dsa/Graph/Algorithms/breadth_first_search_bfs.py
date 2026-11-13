def breadth_first_search(graph, start_node=None):
    if not graph:
        return []
    if start_node is None:
        start_node = next(iter(graph))
    if start_node not in graph:
        return []
    visited = [start_node]
    queue = [start_node]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
    return order