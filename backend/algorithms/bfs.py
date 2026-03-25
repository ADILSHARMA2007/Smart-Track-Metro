"""
Breadth-First Search Algorithm
Finds path with minimum number of stations (hops).
"""

from collections import deque


def bfs(graph: dict, start: str, end: str) -> dict:
    """
    BFS pathfinding - finds path with minimum number of stations.

    Returns:
        dict with keys: path, total_stops, total_cost, nodes_explored, explored_order
    """
    if start not in graph or end not in graph:
        return {
            "path": [],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 0,
            "explored_order": [],
            "error": "Station not found in graph"
        }

    if start == end:
        return {
            "path": [start],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 1,
            "explored_order": [start],
        }

    visited = set()
    queue = deque()
    queue.append((start, [start], 0))
    visited.add(start)
    explored_order = [start]
    nodes_explored = 0

    while queue:
        current, path, cost = queue.popleft()
        nodes_explored += 1

        for neighbor, weight in graph.get(current, {}).items():
            if neighbor not in visited:
                visited.add(neighbor)
                explored_order.append(neighbor)
                new_path = path + [neighbor]
                new_cost = cost + weight

                if neighbor == end:
                    return {
                        "path": new_path,
                        "total_stops": len(new_path) - 1,
                        "total_cost": round(new_cost, 2),
                        "nodes_explored": nodes_explored,
                        "explored_order": explored_order,
                    }

                queue.append((neighbor, new_path, new_cost))

    return {
        "path": [],
        "total_stops": 0,
        "total_cost": 0,
        "nodes_explored": nodes_explored,
        "explored_order": explored_order,
        "error": "No path found"
    }
