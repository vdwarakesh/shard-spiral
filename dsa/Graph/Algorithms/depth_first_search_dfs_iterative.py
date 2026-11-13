def depth_first_search(graph, start_node=None):
    if not graph:
        return []
    if start_node is None:
        start_node = next(iter(graph))
    if start_node not in graph:
        return []
    visited = []
    stack = [start_node]
    order = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.append(node)
            order.append(node)
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    return order